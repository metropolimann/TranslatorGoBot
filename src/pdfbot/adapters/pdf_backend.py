# src/pdfbot/adapters/pdf_backend.py
from pathlib import Path
import pymupdf
from pdfbot.core.exceptions import SplitError
from pdfbot.logging_setup import logger


class PdfBackend:
    """Wrapper around PyMuPDF to isolate PDF operations."""

    @staticmethod
    def get_page_count(pdf_path: Path) -> int:
        """Returns the total number of pages in a PDF."""
        try:
            with pymupdf.open(pdf_path) as doc:
                return len(doc)
        except Exception as e:
            logger.error(f"Failed to open PDF {pdf_path}: {e}")
            raise SplitError(f"Could not open PDF: {e}") from e

    @staticmethod
    def extract_and_save_pages(
        pdf_path: Path, start_page: int, end_page: int, output_path: Path
    ) -> None:
        """
        Extracts pages from start_page to end_page (1-indexed, inclusive)
        and saves them to output_path.
        """
        try:
            # Open the source document
            with pymupdf.open(pdf_path) as source_doc:
                # Create a new empty document for the pack
                with pymupdf.open() as new_doc:
                    # PyMuPDF uses 0-based indexing, so we subtract 1
                    # end_page in fitz is exclusive, so we don't subtract 1 from it
                    new_doc.insert_pdf(
                        source_doc,
                        from_page=start_page - 1,
                        to_page=end_page - 1
                    )
                    
                    # Save the new document
                    new_doc.save(output_path, garbage=3, deflate=True)
                    
            logger.debug(f"Saved pack: {output_path.name} (pages {start_page}-{end_page})")
            
        except Exception as e:
            logger.error(f"Failed to split PDF {pdf_path} at pages {start_page}-{end_page}: {e}")
            raise SplitError(f"Failed to split PDF: {e}") from e
    @staticmethod
    def extract_text(pdf_path: Path) -> str:
        """Extracts all text from a PDF as a single string."""
        try:
            with pymupdf.open(pdf_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text("text") + "\n\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise SplitError(f"Could not extract text: {e}") from e