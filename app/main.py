import logging
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List

from .config import settings
from .models import SearchResponse, SourceStatus, ManualListingCreate, ListingItem
from .service import search_service

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pricewatcher")

app = FastAPI(
    title="PriceWatcher GR - Μηχανή Αναζήτησης Μεταχειρισμένων",
    description="Ολοκληρωμένη πλατφόρμα αναζήτησης και σύγκρισης μεταχειρισμένων προϊόντων από ελληνικές πλατφόρμες.",
    version="1.0.0"
)

# CORS Middleware για ευελιξία
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "PriceWatcher GR",
        "version": "1.0.0"
    }

@app.get("/api/sources", response_model=List[SourceStatus])
def get_sources():
    """Επιστροφή πληροφοριών, νομικών περιορισμών και robots.txt για κάθε πλατφόρμα."""
    return search_service.get_sources_info()

@app.post("/api/manual", response_model=ListingItem, status_code=status.HTTP_201_CREATED)
def add_manual_ad(item: ManualListingCreate):
    """
    Χειροκίνητη καταχώριση αγγελίας (π.χ. από Facebook Marketplace)
    για ενιαία σύγκριση τιμών.
    """
    try:
        return search_service.add_manual_listing(item)
    except Exception as e:
        logger.error("Σφάλμα προσθήκης χειροκίνητης αγγελίας: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/search", response_model=SearchResponse)
def search_listings(
    q: str = Query(..., min_length=1, description="Αναζήτηση προϊόντος (π.χ. iPhone 13, Thinkpad)"),
    min_price: Optional[float] = Query(None, ge=0, description="Ελάχιστη τιμή σε €"),
    max_price: Optional[float] = Query(None, ge=0, description="Μέγιστη τιμή σε €"),
    platform: Optional[str] = Query("all", description="Φίλτρο πλατφόρμας (all, insomnia, vendora, zer, ebyte, pcarena, facebook)"),
    location: Optional[str] = Query("all", description="Φίλτρο πόλης / τοποθεσίας"),
    only_clear: bool = Query(False, description="Εμφάνιση μόνο αγγελιών με σαφή τιμή"),
    sort: str = Query("price_asc", description="Ταξινόμηση: price_asc (χαμηλότερη προς υψηλότερη), price_desc, newest")
):
    """
    Κεντρικό endpoint αναζήτησης σε όλες τις επιτρεπόμενες πλατφόρμες με παράλληλη εκτέλεση,
    κανονικοποίηση τιμών, φιλτράρισμα και προεπιλεγμένη ταξινόμηση από τη χαμηλότερη τιμή.
    """
    return search_service.search(
        query=q,
        min_price=min_price,
        max_price=max_price,
        platform=platform,
        location=location,
        only_clear_price=only_clear,
        sort_by=sort
    )

# Σερβίρισμα στατικών αρχείων και Frontend
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
    return FileResponse(str(index_file))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
