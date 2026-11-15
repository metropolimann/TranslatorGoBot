# src/pdfbot/core/constants.py
from enum import Enum

class TaskType(str, Enum):
    """The types of tasks recorded in the history database."""
    SPLIT = "split"
    TRANSLATE = "translate"
    EXPORT = "export"

class LanguageCode(str, Enum):
    """Supported language codes for translation (ISO-639-1)."""
    EN = "en"
    FR = "fr"
    AR = "ar"
    ES = "es"
    DE = "de"
    ZH = "zh"
    RU = "ru"
    # Add more as needed; the GUI will read from this enum

# ---------------------------------------------------------------------------
# Folder names (relative to DATA_DIR)
# ---------------------------------------------------------------------------
# Used by splitter.py to create the output folder
PACKS_DIR_NAME = "packs"

# Used by translator.py to store the generated PDFs
TRANSLATED_DIR_NAME = "RawTranslatedMaterial"

# ---------------------------------------------------------------------------
# File names & formats
# ---------------------------------------------------------------------------
MANIFEST_FILENAME = "manifest.json"
HISTORY_DB_FILENAME = "history.db"

# Naming convention for split PDFs: <identifier>_<basename>_p<start>-<end>.pdf
PACK_FILENAME_TEMPLATE = "{identifier}_{basename}_p{start:03d}-{end:03d}.pdf"

# Naming convention for translated PDFs: <identifier>_p<start>-<end>_<tgt>.pdf
TRANSLATED_FILENAME_TEMPLATE = "{identifier}_p{start:03d}-{end:03d}_{tgt}.pdf"