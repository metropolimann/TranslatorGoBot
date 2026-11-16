# src/pdfbot/services/translator.py
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from pdfbot.adapters.pdf_backend import PdfBackend
from pdfbot.adapters.translator_backend import TranslatorBackend
from pdfbot.config import settings
from pdfbot.core.constants import TRANSLATED_DIR_NAME, TRANSLATED_FILENAME_TEMPLATE
from pdfbot.core.exceptions import TranslateError
from pdfbot.core.models import TranslateRequest, TranslateResult
from pdfbot.logging_setup import logger


class TranslatorService:
    """Business logic for translating a PDF pack and saving the result."""

    @staticmethod
    def translate_pack(request: TranslateRequest, keep_open: bool = False) -> TranslateResult:
        pdf_path = request.pack_path.resolve()
        if not pdf_path.exists():
            raise TranslateError(f"File not found: {pdf_path}")

        # 1. Extract text from the PDF
        logger.info(f"Extracting text from {pdf_path.name}...")
        original_text = PdfBackend.extract_text(pdf_path)
        
        if not original_text:
            raise TranslateError("The PDF contains no readable text (it might be scanned images).")

        # 2. Translate the text (Chunking logic for Google's limits)
        # Google Translate handles ~5000 chars well. We'll chunk at 4500.
        chunk_size = settings.translate_chunk_chars
        text_chunks = [original_text[i:i+chunk_size] for i in range(0, len(original_text), chunk_size)]
        
        translated_chunks = []
        total_chars = 0
        
        for i, chunk in enumerate(text_chunks):
            logger.info(f"Translating chunk {i+1}/{len(text_chunks)}...")
            translated_chunk = TranslatorBackend.translate_text(
                text=chunk,
                src_lang=request.src_lang.value,
                tgt_lang=request.tgt_lang.value,
                keep_open=(keep_open and i == len(text_chunks) - 1) # Only pause on the LAST chunk!
            )
            translated_chunks.append(translated_chunk)
            total_chars += len(translated_chunk)
            
            # Optional delay to avoid captchas
            if i < len(text_chunks) - 1:
                import time
                time.sleep(settings.translate_delay_seconds)

        final_translated_text = "\n\n".join(translated_chunks)

        # 3. Save to PDF
        output_dir = settings.data_dir / TRANSLATED_DIR_NAME
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract page range for the filename (from the pack name)
        # Pack name format: ID_basename_pXXX-YYY.pdf
        stem_parts = pdf_path.stem.split("_p")
        page_range = stem_parts[-1] if len(stem_parts) > 1 else "unknown"
        
        filename = TRANSLATED_FILENAME_TEMPLATE.format(
            identifier=request.identifier,
            start=page_range.split("-")[0],
            end=page_range.split("-")[1] if "-" in page_range else "000",
            tgt=request.tgt_lang.value
        )
        output_pdf_path = output_dir / filename

        logger.info(f"Generating translated PDF: {filename}...")
        TranslatorService._generate_pdf(final_translated_text, output_pdf_path, request)

        return TranslateResult(
            identifier=request.identifier,
            output_pdf=output_pdf_path,
            src_lang=request.src_lang,
            tgt_lang=request.tgt_lang,
            characters_translated=total_chars
        )

    @staticmethod
    def _generate_pdf(text: str, output_path: Path, request: TranslateRequest) -> None:
        """Helper to render the translated text into a PDF."""
        # Use a standard font. (You can add custom fonts to resources/fonts later if needed)
        # ReportLab has built-in Helvetica, but for full Unicode (Arabic, etc), you need a TTF.
        # For now, we'll use standard formatting.
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Create a custom style
        style = ParagraphStyle(
            name='TranslatedText',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=10,
        )

        # ReportLab's Paragraph needs text to be escaped properly
        story = []
        
        # Split text by double newline into paragraphs
        paragraphs = text.split("\n\n")
        for p_text in paragraphs:
            if p_text.strip():
                # Escape HTML characters just in case
                safe_text = p_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(safe_text, style))
                story.append(Spacer(1, 10))
                
        doc.build(story)
        logger.debug(f"Saved PDF to {output_path}")