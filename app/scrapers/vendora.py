import logging
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import ListingItem
from ..config import settings
from ..utils import normalize_price, clean_text, extract_greek_location, generate_item_id

logger = logging.getLogger(__name__)

class VendoraScraper(BaseScraper):
    id = "vendora"
    name = "Vendora"
    base_url = "https://vendora.gr/"
    legal_notes = (
        "Πλατφόρμα αγγελιών μεταχειρισμένων. Επιτρέπει /items/*/*.html στο robots.txt και απαγορεύει "
        "εσωτερικά APIs (/api/, /partner-api/). Η ανάκτηση εκτελείται με σεβασμό στα όρια αιτημάτων "
        "της ιστοσελίδας, χωρίς αποθήκευση προσωπικών δεδομένων και με απευθείας ανακατεύθυνση."
    )
    robots_txt_status = "Allow: /items/*/*.html$ | Disallow: /api/, /partner-api/"
    api_available = False

    def is_enabled(self) -> bool:
        return settings.ENABLE_VENDORA

    def get_direct_search_url(self, query: str) -> str:
        return f"https://vendora.gr/items?q={quote(query.strip())}"

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
                logger.warning("Vendora returned status %s for query %s", resp.status_code, query)
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select('a.card-product[href*="/items/"]')
            results = []

            for card in cards:
                if len(results) >= max_results:
                    break

                raw_url = card.get("href", "")
                if not raw_url.endswith(".html"):
                    continue

                url = urljoin(self.base_url, raw_url)

                title_el = card.select_one(".title span.body-m, .title, p.title")
                title = clean_text(title_el.get_text(strip=True)) if title_el else ""
                if not title:
                    continue

                price_el = card.select_one(".subtitle .label-l, .subtitle, p.subtitle")
                price_text = price_el.get_text(" ", strip=True) if price_el else ""
                price_val, price_fmt, is_clear = normalize_price(price_text)

                img_el = card.select_one("picture img, img")
                img_url = ""
                if img_el:
                    img_url = img_el.get("src") or img_el.get("data-src", "")
                    if not img_url:
                        source_el = card.select_one("picture source")
                        if source_el and source_el.get("srcset"):
                            img_url = source_el.get("srcset").split()[0]

                item_id = generate_item_id(self.id, url, title)

                results.append(
                    ListingItem(
                        id=item_id,
                        title=title,
                        price=price_val,
                        price_formatted=price_fmt,
                        is_price_clear=is_clear,
                        description="Αγγελία ιδιώτη στο Vendora (Αποστολή με Box Now / ΕΛΤΑ Courier / Συνάντηση)",
                        location="Πανελλαδικά / Box Now & Courier",
                        platform=self.id,
                        platform_name=self.name,
                        date_published=None,
                        url=url,
                        image_url=img_url if img_url else None
                    )
                )

            return results
        except Exception as e:
            logger.error("Error scraping Vendora: %s", e)
            return []
