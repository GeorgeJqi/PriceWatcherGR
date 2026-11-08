from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ListingItem(BaseModel):
    id: str = Field(..., description="Μοναδικό αναγνωριστικό αγγελίας")
    title: str = Field(..., description="Τίτλος αγγελίας / προϊόντος")
    price: Optional[float] = Field(None, description="Κανονικοποιημένη τιμή σε Ευρώ (€)")
    price_formatted: str = Field(..., description="Εμφανιζόμενη μορφή τιμής")
    is_price_clear: bool = Field(True, description="Αν η τιμή είναι σαφής και έγκυρη")
    description: Optional[str] = Field(None, description="Σύντομη περιγραφή / χαρακτηριστικά")
    location: str = Field("Πανελλαδικά / Αποστολή", description="Τοποθεσία ή διαθεσιμότητα")
    platform: str = Field(..., description="Αναγνωριστικό πλατφόρμας (insomnia, vendora, zer, ebyte, pcarena, facebook)")
    platform_name: str = Field(..., description="Φιλικό όνομα πλατφόρμας")
    date_published: Optional[str] = Field(None, description="Ημερομηνία ανάρτησης/ενημέρωσης")
    url: str = Field(..., description="Απευθείας σύνδεσμος προς την αρχική αγγελία")
    image_url: Optional[str] = Field(None, description="URL εικόνας προϊόντος")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Χρόνος ανάκτησης")

class SourceStatus(BaseModel):
    id: str
    name: str
    base_url: str
    direct_search_url: str
    status: str = Field("active", description="active, restricted, direct_link_only, error")
    legal_notes: str = Field(..., description="Περιγραφή όρων χρήσης, robots.txt και περιορισμών")
    robots_txt_status: str = Field(..., description="Κατάσταση robots.txt για bots")
    api_available: bool = Field(False, description="Διαθεσιμότητα επίσημου ανοιχτού API")
    item_count: int = 0
    error_message: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[ListingItem]
    sources_status: List[SourceStatus]
    timestamp: str
    execution_time_seconds: float
    disclaimer: str = (
        "Προσοχή: Οι τιμές και η διαθεσιμότητα των προϊόντων ενδέχεται να αλλάξουν ανά πάσα στιγμή. "
        "Η τελική και έγκυρη πληροφορία βρίσκεται πάντα στην αρχική σελίδα της κάθε αγγελίας. "
        "Η εφαρμογή δεν αποθηκεύει προσωπικά δεδομένα πωλητών."
    )

class ManualListingCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=250)
    price: Optional[float] = Field(None, ge=0)
    url: str = Field(..., min_length=5)
    location: Optional[str] = "Πανελλαδικά"
    description: Optional[str] = None
    platform: str = Field("facebook_manual", description="Πλατφόρμα προέλευσης (π.χ. facebook_manual)")
