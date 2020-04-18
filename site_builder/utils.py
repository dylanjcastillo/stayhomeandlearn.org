from pathlib import Path

SRC_DIR = Path(__file__).parent
TEMPLATE_DIR = SRC_DIR / "template"
SITE_DIR = SRC_DIR / "site"
DATA_DIR = SRC_DIR / "data"

IGNORED_FILES = ["template.html", ".DS_Store"]
INVALIDATIONS = ["/index.html", "/css/style.css"]

LISTS_MAPPING = {
    "learning_resources": "&#128218; Learning Resources",
    "productivity": "&#128187; Productivity",
    "health": "&#x1F3CB; Health & Fitness",
    "entertainment": "&#x1f3ae; Entertainment",
}

CONTENT_TYPE_MAPPING = {
    ".css": "text/css",
    ".html": "text/html",
    ".jpg": "image/jpeg",
    ".xml": "text/xml",
}
