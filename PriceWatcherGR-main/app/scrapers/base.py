import abc
from typing import List, Optional
from ..models import ListingItem, SourceStatus

class BaseScraper(abc.ABC):
    id: str = "base"
    name: str = "Base Scraper"
    base_url: str = ""
    legal_notes: str = ""
    robots_txt_status: str = ""
    api_available: bool = False

    @abc.abstractmethod
    def is_enabled(self) -> bool:
        """Επιστρέφει true αν ο scraper είναι ενεργοποιημένος στις ρυθμίσεις."""
        pass

    @abc.abstractmethod
    def get_direct_search_url(self, query: str) -> str:
        """Επιστρέφει τον σύνδεσμο απευθείας αναζήτησης στην πλατφόρμα."""
        pass

    @abc.abstractmethod
    def scrape(self, query: str, max_results: int = 30) -> List[ListingItem]:
        """Εκτελεί τη συλλογή αγγελιών και επιστρέφει κανονικοποιημένα αποτελέσματα."""
        pass

    def get_status_info(self, item_count: int = 0, error: Optional[str] = None) -> SourceStatus:
        status_val = "active"
        if error:
            status_val = "error"
        elif not self.is_enabled():
            status_val = "disabled"
            
        return SourceStatus(
            id=self.id,
            name=self.name,
            base_url=self.base_url,
            direct_search_url=self.get_direct_search_url(""),
            status=status_val,
            legal_notes=self.legal_notes,
            robots_txt_status=self.robots_txt_status,
            api_available=self.api_available,
            item_count=item_count,
            error_message=error
        )
