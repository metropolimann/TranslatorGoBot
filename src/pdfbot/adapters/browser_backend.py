# src/pdfbot/adapters/browser_backend.py
from contextlib import contextmanager
from typing import Generator
from playwright.sync_api import sync_playwright, Page, BrowserContext

from pdfbot.config import settings
from pdfbot.core.exceptions import TranslateError
from pdfbot.logging_setup import logger


class BrowserBackend:
    """Handles launching and closing the Brave browser."""

    @staticmethod
    @contextmanager
    def get_page(keep_open: bool = False) -> Generator[Page, None, None]: # <--- Added keep_open
        """
        Context manager that launches Brave and yields a Playwright Page.
        """
        logger.info("Launching Brave browser...")
        
        try:
            with sync_playwright() as p:
                launch_args = {
                    "headless": settings.headless,
                    "user_data_dir": str(settings.browser_profile_dir),
                    "args": [
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                    ]
                }

                if settings.brave_path:
                    launch_args["executable_path"] = str(settings.brave_path)
                else:
                    launch_args["channel"] = "brave"

                context: BrowserContext = p.chromium.launch_persistent_context(**launch_args)
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(settings.browser_timeout * 1000)
                
                yield page
                
                # <--- Added pause logic here
                if keep_open:
                    print("\n" + "="*50)
                    print("🛑 BROWSER IS BEING HELD OPEN.")
                    print("Do your human-interaction stuff in Brave.")
                    print("Press [ENTER] in this terminal when you are done to close it.")
                    print("="*50 + "\n")
                    input()
                
                logger.debug("Closing browser...")
                context.close()
                
        except Exception as e:
            logger.error(f"Browser error: {e}")
            raise TranslateError(f"Failed to launch or use the browser: {e}") from e