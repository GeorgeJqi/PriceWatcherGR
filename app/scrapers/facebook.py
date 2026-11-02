import logging
from urllib.parse import quote
from typing import List

from .base import BaseScraper
from ..models import ListingItem, SourceStatus
from ..config import settings

logger = logging.getLogger(__name__)

class FacebookMarketplaceHandler(BaseScraper):
    id = "facebook"
    name = "Facebook Marketplace"
    base_url = "https://www.facebook.com/marketplace/"
    legal_notes = (
        "Η αυτοματοποιημένη συλλογή δεδομένων (scraping) στο Facebook Marketplace απαγορεύεται ρητά "
        "από τους Όρους της Meta (Meta Automated Data Collection Terms) και το robots.txt (Disallow: /). "
        "Απαιτείται σύνδεση χρήστη (login) και η Meta δεν παρέχει δημόσιο search API. "
        "Ως νόμιμη εναλλακτική παρέχεται: 1) Άμεσος σύνδεσμος αναζήτησης με προ-συμπληρωμένο το προϊόν, "
        "και 2) Δυνατότητα χειροκίνητης καταχώρισης αγγελίας για σύγκριση."
    )
    robots_txt_status = "Disallow: / (Ρητή απαγόρευση bots & crawlers)"
    api_available = False

    def is_enabled(self) -> bool:
        return settings.ENABLE_FACEBOOK_DIRECT

    def get_direct_search_url(self, query: str) -> str:
        if not query.strip():
            return "https://www.facebook.com/marketplace/"
        return f"https://www.facebook.com/marketplace/search/?query={quote(query.strip())}"

    def scrape(self, query: str, max_results: int = 30) -> List[ListingItem]:
        # Σε πλήρη συμμόρφωση με τις απαιτήσεις του χρήστη, τους όρους της Meta και το robots.txt,
        # ΔΕΝ παρακάμπτουμε login, CAPTCHA ή ελέγχους πρόσβασης.
        # Η μέθοδος επιστρέφει κενή λίστα αυτόματης συλλογής και το σύστημα παραπέμπει σε άμεσο link και χειροκίνητη εισαγωγή.
        logger.info(
            "Facebook Marketplace: Παράλειψη αυτοματοποιημένης συλλογής λόγω Meta ToS & robots.txt. "
            "Παρέχεται απευθείας σύνδεσμος αναζήτησης: %s",
            self.get_direct_search_url(query)
        )
        return []

    def get_status_info(self, item_count: int = 0, error: str = None) -> SourceStatus:
        return SourceStatus(
            id=self.id,
            name=self.name,
            base_url=self.base_url,
            direct_search_url=self.get_direct_search_url(""),
            status="direct_link_only",
            legal_notes=self.legal_notes,
            robots_txt_status=self.robots_txt_status,
            api_available=self.api_available,
            item_count=item_count,
            error_message="Απαιτείται σύνδεση & απαγορεύεται από τους όρους της Meta. Χρησιμοποιήστε τον άμεσο σύνδεσμο ή χειροκίνητη εισαγωγή."
        )
