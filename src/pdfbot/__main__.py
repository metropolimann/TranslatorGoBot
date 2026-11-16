# src/pdfbot/__main__.py
import argparse
import sys
from pathlib import Path

from pdfbot.logging_setup import setup_logging, logger
from pdfbot.core.models import SplitRequest, TranslateRequest
from pdfbot.core.exceptions import PdfBotError
from pdfbot.core.constants import TaskType, LanguageCode
from pdfbot.services.splitter import PdfSplitter
from pdfbot.services.translator import TranslatorService
from pdfbot.services.history import HistoryService
from pdfbot.services.sync import sync_all_unsynced
from pdfbot.db.session import init_db


def main() -> None:
    """Entry point for the pdfbot CLI."""
    setup_logging()
    init_db()  # Ensure database and tables exist on startup

    parser = argparse.ArgumentParser(
        prog="pdfbot",
        description="PDF -> Translate -> Archive Bot",
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Subcommand: split ---
    split_parser = subparsers.add_parser("split", help="Split a PDF into page packs")
    split_parser.add_argument("pdf", type=Path, help="Path to the source PDF file")
    split_parser.add_argument("--start", "-s", type=int, required=True, dest="n1", help="First page (1-indexed)")
    split_parser.add_argument("--end", "-e", type=int, required=True, dest="n2", help="Last page (inclusive)")
    split_parser.add_argument("--size", "-m", type=int, default=25, help="Pages per pack (default: 25)")
    split_parser.add_argument("--id", "-i", type=str, required=True, dest="identifier", help="Identifier prefix for filenames")

    # --- Subcommand: translate ---
    translate_parser = subparsers.add_parser("translate", help="Translate a PDF pack")
    translate_parser.add_argument("pdf", type=Path, help="Path to the split PDF pack")
    translate_parser.add_argument("--src", "-s", type=str, default="en", help="Source language (e.g. en)")
    translate_parser.add_argument("--tgt", "-t", type=str, default="fr", help="Target language (e.g. fr)")
    translate_parser.add_argument("--id", "-i", type=str, required=True, dest="identifier", help="Identifier")
    translate_parser.add_argument("--keep-open", "-k", action="store_true", help="Keep browser open for human interaction")

    # --- Subcommand: history ---
    history_parser = subparsers.add_parser("history", help="View task history")
    history_parser.add_argument("--limit", "-l", type=int, default=10, help="Number of records to show")

    # Parse arguments
    args = parser.parse_args()

    try:
        if args.command == "split":
            request = SplitRequest(
                pdf_path=args.pdf,
                n1=args.n1,
                n2=args.n2,
                m=args.size,
                identifier=args.identifier,
            )
            result = PdfSplitter.split(request)
            
            # Log the successful task to the database!
            HistoryService.log_task(
                task_type=TaskType.SPLIT,
                meta_data={
                    "source_file": str(args.pdf),
                    "pages": f"{args.n1}-{args.n2}",
                    "packs_created": result.total_packs
                }
            )
            
            print(f"\n✅ Successfully created {result.total_packs} packs.")
            print(f"📁 Output directory: {result.output_dir}")

        elif args.command == "translate":
            request = TranslateRequest(
                pack_path=args.pdf,
                src_lang=LanguageCode(args.src),
                tgt_lang=LanguageCode(args.tgt),
                identifier=args.identifier
            )
            
            # Execute the translation service
            result = TranslatorService.translate_pack(request, keep_open=args.keep_open)
            
            # Log the task to history
            HistoryService.log_task(
                task_type=TaskType.TRANSLATE,
                meta_data={
                    "source_file": str(args.pdf),
                    "src_lang": args.src,
                    "tgt_lang": args.tgt,
                    "chars": result.characters_translated
                }
            )
            
            print(f"\n✅ Successfully translated pack.")
            print(f"📁 Output file: {result.output_pdf}")

        elif args.command == "history":
            # Try to sync any offline tasks to PostgreSQL first
            sync_all_unsynced()
            
            tasks = HistoryService.list_tasks(limit=args.limit)
            if not tasks:
                print("No tasks found in history.")
                return

            print(f"\n{'ID':<10} | {'Task':<12} | {'Done By':<10} | {'Date':<12} | {'Time':<8} | {'Synced'}")
            print("-" * 75)
            for t in tasks:
                # Shorten UUID for display
                short_id = str(t.id)[:8]
                synced = "✅" if t.is_synced else "⏳"
                print(f"{short_id:<10} | {t.task_type:<12} | {t.done_by:<10} | {t.date} | {t.time.strftime('%H:%M:%S'):<8} | {synced}")
            print()

    except PdfBotError as e:
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()