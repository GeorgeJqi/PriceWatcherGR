import logging
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import ListingItem
from ..config import settings
from ..utils import normalize_price, clean_text, extract_greek_location, generate_item_id

logger = logging.getLogger(__name__)

class InsomniaScraper(BaseScraper):
    id = "insomnia"
    name = "Insomnia Classifieds"
    base_url = "https://www.insomnia.gr/classifieds/"
    legal_notes = (
        "Οι αγγελίες είναι δημόσια προσβάσιμες. Στο robots.txt υπάρχει Disallow: /classifieds/search/ "
        "για crawlers μηχανών αναζήτησης προς αποφυγή crawl traps. Η εφαρμογή πραγματοποιεί ήπια αιτήματα "
        "με caching, χωρίς αποθήκευση στοιχείων πωλητών και με παροχή απευθείας συνδέσμου."
    )
    robots_txt_status = "Disallow: /classifieds/search/ (κανόνας αποφυγής crawl trap)"
    api_available = False

    def is_enabled(self) -> bool:
        return settings.ENABLE_INSOMNIA

    def get_direct_search_url(self, query: str) -> str:
        return f"https://www.insomnia.gr/classifieds/search/?q={quote(query.strip())}"

    def scrape(self, query: str, max_results: int = 30) -> list[ListingItem]:
        if not self.is_enabled() or not query.strip():
            return []

        search_url = self.get_direct_search_url(query)
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "el-GR,el;q=0.9,en;q=0.8"
        }

        try:
            resp = requests.get(search_url, headers=headers, timeout=settings.REQUEST_TIMEOUT_SECONDS)
            if resp.status_code != 200:
                logger.warning("Insomnia returned status %s for query %s", resp.status_code, query)
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".insSrCard")
            results = []

            for card in cards[:max_results]:
                title_el = card.select_one(".insSrCard__title a")
                if not title_el:
                    continue

                title = clean_text(title_el.get_text(strip=True))
                raw_url = title_el.get("href", "")
                url = urljoin(self.base_url, raw_url)

                price_el = card.select_one(".insSrCard__price")
                price_text = price_el.get_text(strip=True) if price_el else ""
                price_val, price_fmt, is_clear = normalize_price(price_text)

                snippet_el = card.select_one(".insSrCard__snippet")
                snippet = clean_text(snippet_el.get_text(strip=True)) if snippet_el else ""

                date_el = card.select_one(".insSrCard__date time")
                date_str = ""
                if date_el:
                    date_str = date_el.get("datetime") or clean_text(date_el.get_text(strip=True))

                img_el = card.select_one(".insSrCard__media img")
                img_url = ""
                if img_el:
                    src = img_el.get("src") or img_el.get("data-src", "")
                    if src.startswith("//"):
                        img_url = "https:" + src
                    elif src.startswith("http"):
                        img_url = src

                location = extract_greek_location(snippet, default="Πανελλαδικά / Αποστολή")
                item_id = generate_item_id(self.id, url, title)

                results.append(
                    ListingItem(
                        id=item_id,
                        title=title,
                        price=price_val,
                        price_formatted=price_fmt,
                        is_price_clear=is_clear,
                        description=snippet,
                        location=location,
                        platform=self.id,
                        platform_name=self.name,
                        date_published=date_str if date_str else None,
                        url=url,
                        image_url=img_url if img_url else None
                    )
                )

            return results
        except Exception as e:
            logger.error("Error scraping Insomnia: %s", e)
            return []
