# src/pdfbot/adapters/translator_backend.py
import urllib.parse
from pdfbot.adapters.browser_backend import BrowserBackend
from pdfbot.core.exceptions import TranslateError
from pdfbot.logging_setup import logger


class TranslatorBackend:
    """Handles translating text by driving Google Translate in a browser."""

    @staticmethod
    def translate_text(text: str, src_lang: str, tgt_lang: str, keep_open: bool = False) -> str: # <--- Added keep_open
        """
        Translates a block of text using Google Translate.
        """
        if not text.strip():
            return ""

        logger.info(f"Translating {len(text)} characters from {src_lang} to {tgt_lang}...")

        # <--- Pass the flag to the browser backend
        with BrowserBackend.get_page(keep_open=keep_open) as page:
            try:
                encoded_text = urllib.parse.quote(text)
                url = f"https://translate.google.com/?sl={src_lang}&tl={tgt_lang}&op=translate&hl=en&text={encoded_text}"
                page.goto(url, wait_until="domcontentloaded")
                
                result_selector = f'span[lang="{tgt_lang}"]'
                page.wait_for_selector(result_selector, state="attached", timeout=15000)
                page.wait_for_timeout(1000)

                result_spans = page.locator(result_selector).all_inner_texts()
                translated_text = "\n".join(result_spans)

                if not translated_text.strip():
                    raise TranslateError("Google Translate returned an empty result.")

                return translated_text.strip()

            except Exception as e:
                error_img = "translation_error.png"
                try:
                    page.screenshot(path=error_img)
                    logger.error(f"Saved error screenshot to {error_img}")
                except:
                    pass
                raise TranslateError(f"Browser automation failed: {e}") from e