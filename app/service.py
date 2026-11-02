import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict
from datetime import datetime
import unicodedata

from .models import ListingItem, SourceStatus, SearchResponse, ManualListingCreate
from .scrapers import get_all_scrapers
from .cache import cache
from .config import settings
from .utils import deduplicate_listings, normalize_price, generate_item_id, is_relevant_item, strip_accents

logger = logging.getLogger(__name__)

# Τοπική αποθήκευση χειροκίνητων αγγελιών χρήστη (π.χ. από Facebook Marketplace)
manual_listings_store: List[ListingItem] = []

class SearchService:
    def __init__(self):
        self.scrapers = get_all_scrapers()

    def add_manual_listing(self, item_in: ManualListingCreate) -> ListingItem:
        """Προσθήκη χειροκίνητης αγγελίας (π.χ. από Facebook Marketplace)"""
        price_val, price_fmt, is_clear = normalize_price(str(item_in.price) if item_in.price is not None else "")
        item_id = generate_item_id(item_in.platform, item_in.url, item_in.title)

        platform_label = "Facebook (Χειροκίνητη)" if item_in.platform.startswith("facebook") else "Χειροκίνητη Εισαγωγή"

        listing = ListingItem(
            id=item_id,
            title=item_in.title.strip(),
            price=price_val,
            price_formatted=price_fmt,
            is_price_clear=is_clear,
            description=item_in.description or "Χειροκίνητα καταχωρημένη αγγελία για σύγκριση τιμών.",
            location=item_in.location or "Πανελλαδικά",
            platform=item_in.platform,
            platform_name=platform_label,
            date_published="Τώρα",
            url=item_in.url.strip(),
            image_url=None,
            last_updated=datetime.now().isoformat()
        )

        manual_listings_store.insert(0, listing)
        return listing

    def get_sources_info(self) -> List[SourceStatus]:
        """Επιστροφή πληροφοριών κατάστασης, νομικών όρων και robots.txt για όλες τις πηγές."""
        statuses = []
        for scraper in self.scrapers:
            statuses.append(scraper.get_status_info())
        return statuses

    def search(
        self,
        query: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        platform: Optional[str] = None,
        location: Optional[str] = None,
        only_clear_price: bool = False,
        sort_by: str = "price_asc"
    ) -> SearchResponse:
        start_time = time.time()
        query_clean = query.strip()
        cache_key = f"search:{query_clean.lower()}"

        # Έλεγχος cache για την ακατέργαστη αναζήτηση
        cached_data = cache.get(cache_key)
        if cached_data:
            all_raw_items, source_statuses = cached_data
            logger.info("Ανάκτηση αποτελεσμάτων από cache για: '%s'", query_clean)
        else:
            all_raw_items = []
            source_statuses = []

            # Εκτέλεση συλλογής παράλληλα σε νήματα (ThreadPoolExecutor)
            with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
                future_to_scraper = {
                    executor.submit(s.scrape, query_clean, settings.MAX_RESULTS_PER_SOURCE): s
                    for s in self.scrapers
                }

                for future in as_completed(future_to_scraper):
                    scraper = future_to_scraper[future]
                    try:
                        items = future.result()
                        all_raw_items.extend(items)
                        source_statuses.append(scraper.get_status_info(item_count=len(items)))
                    except Exception as exc:
                        logger.error("Scraper %s απέτυχε με εξαίρεση: %s", scraper.name, exc)
                        source_statuses.append(
                            scraper.get_status_info(item_count=0, error=str(exc))
                        )

            # Αποθήκευση στο cache
            cache.set(cache_key, (all_raw_items, source_statuses), ttl=settings.CACHE_TTL_SECONDS)

        # Συγχώνευση με τυχόν χειροκίνητες αγγελίες χρήστη που ταιριάζουν στο ερώτημα
        matching_manual = []
        if query_clean:
            for m in manual_listings_store:
                if is_relevant_item(query_clean, m.title, m.description or ""):
                    matching_manual.append(m)
        else:
            matching_manual = list(manual_listings_store)

        combined_items = matching_manual + all_raw_items

        # Αφαίρεση διπλοτύπων
        deduped = deduplicate_listings(combined_items)

        # Εφαρμογή φίλτρων και αυστηρού ελέγχου σχετικότητας
        filtered = []
        loc_norm = strip_accents(location) if location and location != "all" else None
        plat_norm = platform.lower() if platform and platform != "all" else None

        for item in deduped:
            # 1. Έλεγχος συνάφειας: Απορρίπτουμε προϊόντα που δεν περιέχουν τα ζητούμενα κριτήρια (π.χ. Dell laptop όταν ψάχνουμε iphone 17)
            if query_clean and not is_relevant_item(query_clean, item.title, item.description or ""):
                continue

            # 2. Φίλτρο πλατφόρμας
            if plat_norm:
                if plat_norm == "facebook":
                    if not item.platform.startswith("facebook"):
                        continue
                elif item.platform != plat_norm:
                    continue

            # 3. Φίλτρο σαφούς τιμής
            if only_clear_price and not item.is_price_clear:
                continue

            # 4. Φίλτρο ελάχιστης τιμής
            if min_price is not None:
                if item.price is None or item.price < min_price:
                    continue

            # 5. Φίλτρο μέγιστης τιμής
            if max_price is not None:
                if item.price is None or item.price > max_price:
                    continue

            # 6. Φίλτρο τοποθεσίας
            if loc_norm:
                item_loc_norm = strip_accents(item.location)
                if loc_norm not in item_loc_norm:
                    continue

            filtered.append(item)

        # Ταξινόμηση αποτελεσμάτων
        # Προεπιλογή: Από τη χαμηλότερη προς την υψηλότερη τιμή (price_asc)
        if sort_by == "price_asc":
            filtered.sort(key=lambda x: (x.price is None, x.price if x.price is not None else float('inf')))
        elif sort_by == "price_desc":
            filtered.sort(key=lambda x: (x.price is None, -(x.price if x.price is not None else 0)))
        elif sort_by == "newest":
            filtered.sort(key=lambda x: x.last_updated, reverse=True)

        elapsed = round(time.time() - start_time, 2)

        return SearchResponse(
            query=query_clean,
            total_results=len(filtered),
            results=filtered,
            sources_status=source_statuses,
            timestamp=datetime.now().isoformat(),
            execution_time_seconds=elapsed
        )

search_service = SearchService()
