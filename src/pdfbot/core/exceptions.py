# src/pdfbot/core/exceptions.py

class PdfBotError(Exception):
    """Base exception for all pdfbot errors."""
    pass


class ConfigError(PdfBotError):
    """Raised when settings are missing, invalid, or contradictory."""
    pass


class SplitError(PdfBotError):
    """Raised when PDF splitting fails (e.g., encrypted PDF, invalid page range)."""
    pass


class TranslateError(PdfBotError):
    """Raised when translation fails (e.g., browser crash, captcha, API quota)."""
    pass


class DBError(PdfBotError):
    """Raised when a database operation fails (SQLite or PostgreSQL)."""
    pass