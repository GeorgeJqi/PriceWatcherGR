import logging
from urllib.parse import quote, urljoin
import requests
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..models import ListingItem
from ..config import settings
from ..utils import normalize_price, clean_text, generate_item_id

logger = logging.getLogger(__name__)

class ZerScraper(BaseScraper):
    id = "zer"
    name = "ZER Shop"
    base_url = "https://www.zer.gr/"
    legal_notes = (
        "Ηλεκτρονικό κατάστημα μεταχειρισμένων και refurbished συσκευών με εγγύηση. "
        "Το αρχείο robots.txt επιτρέπει πλήρως την πρόσβαση (User-agent: * Allow: /). "
        "Δεν απαιτείται σύνδεση ούτε υπάρχουν τεχνικά εμπόδια."
    )
    robots_txt_status = "Allow: / (Πλήρως επιτρεπτή πρόσβαση)"
    api_available = False

    def is_enabled(self) -> bool:
        return settings.ENABLE_ZER

    def get_direct_search_url(self, query: str) -> str:
        return f"https://www.zer.gr/index.php?act=viewCat&keywords={quote(query.strip())}"

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
                logger.warning("ZER Shop returned status %s for query %s", resp.status_code, query)
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".product-thumb")
            results = []

            for card in cards[:max_results]:
                # Αναζήτηση συνδέσμου και τίτλου
                link_el = card.select_one(".caption .name a, a.product-img, h4 a, .name a")
                if not link_el:
                    continue

                raw_url = link_el.get("href", "")
                url = urljoin(self.base_url, raw_url)

                title = link_el.get("title") or clean_text(link_el.get_text(strip=True))
                if not title:
                    img_elem = card.select_one("img")
                    if img_elem and img_elem.get("alt"):
                        title = clean_text(img_elem.get("alt"))

                if not title or "Όμιλος ZER" in title:
                    continue

                # Εξαγωγή τιμής
                price_new = card.select_one(".price-new")
                if price_new:
                    price_text = price_new.get_text(strip=True)
                else:
                    price_el = card.select_one(".price")
                    if price_el:
                        # Αφαίρεση παλιάς τιμής και φόρου για αποφυγή σύγχυσης
                        for unwanted in price_el.select(".price-old, .price-tax"):
                            unwanted.decompose()
                        price_text = price_el.get_text(strip=True)
                    else:
                        price_text = ""

                price_val, price_fmt, is_clear = normalize_price(price_text)

                # Εικόνα
                img_el = card.select_one("img.img-first, img.img-responsive, img")
                img_url = ""
                if img_el:
                    img_url = img_el.get("src") or img_el.get("data-src", "")

                desc_el = card.select_one(".description")
                desc_text = clean_text(desc_el.get_text(strip=True)) if desc_el else "Refurbished / Μεταχειρισμένο με εγγύηση ZER Shop"

                item_id = generate_item_id(self.id, url, title)

                results.append(
                    ListingItem(
                        id=item_id,
                        title=title,
                        price=price_val,
                        price_formatted=price_fmt,
                        is_price_clear=is_clear,
                        description=desc_text,
                        location="Αθήνα / Πανελλαδική Αποστολή",
                        platform=self.id,
                        platform_name=self.name,
                        date_published=None,
                        url=url,
                        image_url=img_url if img_url else None
                    )
                )

            return results
        except Exception as e:
            logger.error("Error scraping ZER Shop: %s", e)
            return []
