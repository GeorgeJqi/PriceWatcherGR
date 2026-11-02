import logging
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import ListingItem
from ..config import settings
from ..utils import normalize_price, clean_text, generate_item_id

logger = logging.getLogger(__name__)

class EByteScraper(BaseScraper):
    id = "ebyte"
    name = "E-Byte.gr"
    base_url = "https://e-byte.gr/"
    legal_notes = (
        "Κατάστημα refurbished ηλεκτρονικών υπολογιστών & laptops στη Θεσσαλονίκη με πανελλαδική αποστολή. "
        "Το αρχείο robots.txt επιτρέπει την πρόσβαση στην κεντρική αναζήτηση προϊόντων (Allow: /), "
        "απαγορεύοντας μόνο επιμέρους facet query filters."
    )
    robots_txt_status = "Allow: / (Κύρια αναζήτηση επιτρεπτή)"
    api_available = False

    def is_enabled(self) -> bool:
        return settings.ENABLE_EBYTE

    def get_direct_search_url(self, query: str) -> str:
        return f"https://e-byte.gr/?s={quote(query.strip())}&post_type=product"

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
                logger.warning("E-Byte returned status %s for query %s", resp.status_code, query)
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".product-grid-item, .product.type-product")
            results = []

            for card in cards[:max_results]:
                link_el = card.select_one(".wd-product-img-link, a.woocommerce-LoopProduct-link, h3 a, h2 a")
                if not link_el:
                    continue

                raw_url = link_el.get("href", "")
                url = urljoin(self.base_url, raw_url)

                title_el = card.select_one(".wd-entities-title a, .woocommerce-loop-product__title, h3 a, h2 a")
                title = clean_text(title_el.get_text(strip=True)) if title_el else ""
                if not title:
                    title = clean_text(link_el.get("aria-label", ""))

                if not title:
                    continue

                # Εξαγωγή τιμής (προτίμηση στην τιμή προσφοράς αν υπάρχει)
                price_el = card.select_one(".price ins .woocommerce-Price-amount, ins .woocommerce-Price-amount")
                if not price_el:
                    price_el = card.select_one(".price .woocommerce-Price-amount")

                price_text = price_el.get_text(strip=True) if price_el else ""
                price_val, price_fmt, is_clear = normalize_price(price_text)

                img_el = card.select_one("img")
                img_url = ""
                if img_el:
                    img_url = img_el.get("data-src") or img_el.get("src", "")
                    if img_url.startswith("data:"):
                        img_url = img_el.get("data-src", "")

                item_id = generate_item_id(self.id, url, title)

                results.append(
                    ListingItem(
                        id=item_id,
                        title=title,
                        price=price_val,
                        price_formatted=price_fmt,
                        is_price_clear=is_clear,
                        description="Refurbished Προϊόν με Εγγύηση & Τεχνικό Έλεγχο E-Byte",
                        location="Θεσσαλονίκη / Πανελλαδική Αποστολή",
                        platform=self.id,
                        platform_name=self.name,
                        date_published=None,
                        url=url,
                        image_url=img_url if img_url else None
                    )
                )

            return results
        except Exception as e:
            logger.error("Error scraping E-Byte: %s", e)
            return []
