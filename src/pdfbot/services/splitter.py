# src/pdfbot/services/splitter.py
import json
from pathlib import Path

from pdfbot.adapters.pdf_backend import PdfBackend
from pdfbot.config import settings
from pdfbot.core.constants import PACKS_DIR_NAME, MANIFEST_FILENAME, PACK_FILENAME_TEMPLATE
from pdfbot.core.exceptions import SplitError
from pdfbot.core.models import SplitRequest, SplitResult
from pdfbot.logging_setup import logger


class PdfSplitter:
    """Business logic for splitting PDFs into page packs."""

    @staticmethod
    def split(request: SplitRequest) -> SplitResult:
        """Executes the split request and returns the result."""
        
        pdf_path = request.pdf_path.resolve()
        if not pdf_path.exists():
            raise SplitError(f"File not found: {pdf_path}")

        # 1. Get total pages to validate the request
        total_pages = PdfBackend.get_page_count(pdf_path)
        if request.n1 > total_pages:
            raise SplitError(
                f"Start page ({request.n1}) is greater than the PDF's total pages ({total_pages})."
            )

        # Clamp n2 to the total number of pages if the user went too high
        actual_n2 = min(request.n2, total_pages)
        if actual_n2 != request.n2:
            logger.warning(
                f"Requested end page ({request.n2}) exceeds PDF length. "
                f"Clamping to {actual_n2}."
            )

        # 2. Prepare the output directory
        output_dir = settings.data_dir / PACKS_DIR_NAME
        output_dir.mkdir(parents=True, exist_ok=True)

        # 3. Calculate packs and extract
        created_files = []
        manifest_data = []
        basename = pdf_path.stem  # filename without extension

        logger.info(f"Starting split of '{pdf_path.name}' (pages {request.n1}-{actual_n2} into packs of {request.m})")

        current_start = request.n1
        while current_start <= actual_n2:
            # Calculate the end page for this chunk
            current_end = min(current_start + request.m - 1, actual_n2)

            # Generate the filename
            filename = PACK_FILENAME_TEMPLATE.format(
                identifier=request.identifier,
                basename=basename,
                start=current_start,
                end=current_end,
            )
            output_path = output_dir / filename

            # Call the adapter to physically do the work
            PdfBackend.extract_and_save_pages(
                pdf_path=pdf_path,
                start_page=current_start,
                end_page=current_end,
                output_path=output_path,
            )

            # Track results
            created_files.append(output_path)
            manifest_data.append({
                "filename": filename,
                "start_page": current_start,
                "end_page": current_end,
                "page_count": (current_end - current_start) + 1,
            })

            # Move the starting point to the next chunk
            current_start = current_end + 1

        # 4. Write the manifest.json
        manifest_path = output_dir / MANIFEST_FILENAME
        manifest_content = {
            "source_file": pdf_path.name,
            "identifier": request.identifier,
            "requested_range": [request.n1, request.n2],
            "actual_range": [request.n1, actual_n2],
            "pack_size": request.m,
            "packs": manifest_data,
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_content, f, indent=2)

        logger.info(f"Successfully created {len(created_files)} packs in {output_dir}")

        # 5. Return the result
        return SplitResult(
            identifier=request.identifier,
            output_dir=output_dir,
            created_files=created_files,
            total_packs=len(created_files),
        )