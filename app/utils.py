import re
import hashlib
import unicodedata
from typing import Optional, Tuple, List
from .models import ListingItem

GREEK_LOCATIONS = [
    "Αθήνα", "Θεσσαλονίκη", "Πειραιάς", "Πάτρα", "Ηράκλειο", "Λάρισα",
    "Βόλος", "Ιωάννινα", "Τρίκαλα", "Χαλκίδα", "Σέρρες", "Αλεξανδρούπολη",
    "Ξάνθη", "Κατερίνη", "Καλαμάτα", "Καβάλα", "Χανιά", "Ρόδος", "Κέρκυρα",
    "Αγρίνιο", "Κομοτηνή", "Λαμία", "Δράμα", "Κοζάνη", "Καρδίτσα", "Κόρινθος",
    "Μυτιλήνη", "Χίος", "Βέροια", "Ρέθυμνο", "Πτολεμαΐδα", "Σύρος", "Σαντορίνη",
    "Μύκονος", "Αττική", "Κεντρική Μακεδονία", "Κρήτη"
]

STOPWORDS = {
    'και', 'για', 'σε', 'με', 'το', 'τα', 'τη', 'τον', 'της', 'του', 'των',
    'απο', 'από', 'and', 'for', 'with', 'the', 'in', 'of'
}

SYNONYMS = {
    'ps5': ['playstation 5', 'playstation5', 'ps 5', 'ps5'],
    'ps4': ['playstation 4', 'playstation4', 'ps 4', 'ps4'],
    'iphone': ['iphone', 'αιφον', 'i-phone'],
    'macbook': ['macbook', 'μακμπουκ', 'mac book'],
    'ipad': ['ipad', 'αϊπαντ', 'i-pad'],
}

def strip_accents(s: str) -> str:
    """Αφαίρεση τόνων για ακριβή σύγκριση ελληνικών λέξεων."""
    if not s:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    ).lower()

def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def normalize_price(price_str: Optional[str]) -> Tuple[Optional[float], str, bool]:
    """
    Κανονικοποίηση τιμής σε ευρώ (€).
    Επιστρέφει (αριθμητική τιμή σε float, μορφοποιημένη συμβολοσειρά, εγκυρότητα/σαφήνεια).
    """
    if not price_str:
        return None, "Χωρίς σαφή τιμή", False
    
    raw = clean_text(price_str)
    lower_raw = raw.lower()
    if any(k in lower_raw for k in ["ζήτηση", "ανταλλαγή", "συζητήσιμη", "δωρεάν", "επικοινωνία"]):
        return None, raw, False

    cleaned = raw.replace("€", "").replace("EUR", "").replace("euro", "").strip()
    cleaned = re.sub(r'\s+', '', cleaned)
    
    if not cleaned:
        return None, "Χωρίς σαφή τιμή", False

    if '.' in cleaned and ',' in cleaned:
        if cleaned.rfind(',') > cleaned.rfind('.'):
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        cleaned = cleaned.replace(',', '.')
    elif '.' in cleaned:
        parts = cleaned.split('.')
        if len(parts) == 2 and len(parts[1]) == 3:
            cleaned = parts[0] + parts[1]

    m = re.search(r'([0-9]+(?:\.[0-9]+)?)', cleaned)
    if not m:
        return None, raw, False

    try:
        val = round(float(m.group(1)), 2)
        if val <= 0:
            return None, "0,00 € (Συζητήσιμη)", False
        formatted = f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        return val, formatted, True
    except ValueError:
        return None, raw, False

def extract_greek_location(text: Optional[str], default: str = "Πανελλαδικά / Αποστολή") -> str:
    """Αναγνώριση πόλης/περιοχής από το κείμενο της αγγελίας."""
    if not text:
        return default
    
    for loc in GREEK_LOCATIONS:
        pattern = r'\b' + re.escape(loc) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return loc
            
    return default

def generate_item_id(platform: str, url: str, title: str) -> str:
    unique_key = f"{platform}:{url}:{title}".encode("utf-8")
    return hashlib.sha256(unique_key).hexdigest()[:12]

def is_relevant_item(query: str, title: str, description: str = "") -> bool:
    """
    Αυστηρός έλεγχος σχετικότητας του αποτελέσματος με το ερώτημα αναζήτησης.
    Αποτρέπει την επιστροφή άσχετων προτεινόμενων προϊόντων ή γενικών κατηγοριών.
    """
    if not query.strip():
        return True
    
    q_norm = strip_accents(query.strip())
    raw_tokens = [t for t in re.split(r'[^a-zA-Z0-9\u0370-\u03ff]+', q_norm) if t]
    tokens = [t for t in raw_tokens if t not in STOPWORDS]
    if not tokens:
        tokens = raw_tokens

    text_norm = strip_accents(f"{title} {description}")

    for token in tokens:
        token_matched = False
        possible_variants = [token]

        for k, v in SYNONYMS.items():
            if token == k:
                possible_variants.extend(v)
            elif token in v:
                possible_variants.append(k)
                possible_variants.extend(v)

        for variant in set(possible_variants):
            pattern = r'(?:^|[^a-zA-Z0-9\u0370-\u03ff])' + re.escape(variant)
            if re.search(pattern, text_norm):
                token_matched = True
                break

        if not token_matched:
            return False

    return True

def deduplicate_listings(items: List[ListingItem]) -> List[ListingItem]:
    seen_urls = set()
    seen_signatures = set()
    unique_items = []

    for item in items:
        clean_url = item.url.split('?')[0].rstrip('/')
        if clean_url in seen_urls:
            continue

        title_norm = re.sub(r'[^a-zA-Z0-9\u0370-\u03ff]', '', item.title.lower())
        sig = f"{item.platform}:{title_norm}:{item.price}"
        if sig in seen_signatures:
            continue

        seen_urls.add(clean_url)
        seen_signatures.add(sig)
        unique_items.append(item)

    return unique_items
