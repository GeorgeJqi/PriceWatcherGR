import logging
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import ListingItem
from ..config import settings
from ..utils import normalize_price, clean_text, generate_item_id

logger = logging.getLogger(__name__)

class PCArenaScraper(BaseScraper):
    id = "pcarena"
    name = "PC Arena"
    base_url = "https://www.pcarena.gr/"
    legal_notes = (
        "Κατάστημα refurbished υπολογιστών & ανταλλακτικών. Στο robots.txt περιλαμβάνεται η οδηγία "
        "Disallow: /*route=product/search προς αποφυγή ευρετηρίασης πολλαπλών αναζητήσεων. "
        "Η εφαρμογή υποστηρίζει ήπια συλλογή με σεβασμό στα αιτήματα και άμεση παραπομπή."
    )
    robots_txt_status = "Disallow: /*route=product/search"
    api_available = False

    def is_enabled(self) -> bool:
        return settings.ENABLE_PCARENA

    def get_direct_search_url(self, query: str) -> str:
        return f"https://www.pcarena.gr/index.php?route=product/search&search={quote(query.strip())}"

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
                logger.warning("PC Arena returned status %s for query %s", resp.status_code, query)
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".product-layout .product-thumb, .product-thumb")
            results = []

            for card in cards[:max_results]:
                t_el = card.select_one(".caption .name a, .name a, h4 a")
                if not t_el:
                    continue

                raw_url = t_el.get("href", "")
                url = urljoin(self.base_url, raw_url)

                title = clean_text(t_el.get_text(strip=True))
                if not title:
                    continue

                # Εξαγωγή τιμής
                price_new = card.select_one(".price-new")
                if price_new:
                    price_text = price_new.get_text(strip=True)
                else:
                    price_el = card.select_one(".price")
                    if price_el:
                        for unwanted in price_el.select(".price-old, .price-tax"):
                            unwanted.decompose()
                        price_text = price_el.get_text(strip=True)
                    else:
                        price_text = ""

                price_val, price_fmt, is_clear = normalize_price(price_text)

                desc_el = card.select_one(".description")
                desc_text = clean_text(desc_el.get_text(strip=True)) if desc_el else "Refurbished Υπολογιστής / Hardware με Εγγύηση PC Arena"

                img_el = card.select_one("img.oc-v4-deferred, img")
                img_url = ""
                if img_el:
                    img_url = img_el.get("data-oc-original") or img_el.get("src", "")
                    if img_url.startswith("data:"):
                        img_url = ""

                item_id = generate_item_id(self.id, url, title)

                results.append(
                    ListingItem(
                        id=item_id,
                        title=title,
                        price=price_val,
                        price_formatted=price_fmt,
                        is_price_clear=is_clear,
                        description=desc_text,
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
            logger.error("Error scraping PC Arena: %s", e)
            return []
