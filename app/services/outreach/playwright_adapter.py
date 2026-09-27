from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from app.config import settings
from app.schemas import ApplicationContext
import logging

logger = logging.getLogger(__name__)

class PlaywrightATSAdapter:
    @staticmethod
    def apply(context: ApplicationContext) -> bool:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                logger.info(f"Navigating to ATS URL: {context.job.url}")
                page.goto(context.job.url, timeout=30000)
                
                # 1. Map standard profile fields using common ATS selectors
                # Greenhouse/Lever typically use name attributes like 'first_name', 'email', 'phone'
                PlaywrightATSAdapter._fill_field(page, ['input[name*="first_name"]', 'input[name*="name"]'], settings.candidate_name)
                PlaywrightATSAdapter._fill_field(page, ['input[name*="email"]'], settings.candidate_email)
                PlaywrightATSAdapter._fill_field(page, ['input[name*="phone"]'], settings.candidate_phone)

                # 2. Upload Artifacts
                if context.resume_pdf_path:
                    PlaywrightATSAdapter._upload_file(page, ['input[type="file"][name*="resume"]', 'input[type="file"]'], context.resume_pdf_path)
                
                if context.cover_letter_pdf_path:
                    PlaywrightATSAdapter._upload_file(page, ['input[type="file"][name*="cover"]'], context.cover_letter_pdf_path)

                # Note: Integration for dynamic <textarea> answering via LLMGateway would loop through
                # textareas here, extract their labels, and call LLMGateway with TaskType.ANSWER_ATS_QUESTION.

                # 3. Submit
                submit_button = page.locator('button[type="submit"], input[type="submit"]').first
                if submit_button.is_visible():
                    submit_button.click()
                    page.wait_for_load_state('networkidle')
                    logger.info("Successfully submitted ATS form.")
                else:
                    logger.warning("Submit button not found. Manual intervention required.")
                    return False

                return True

            except PlaywrightTimeoutError:
                logger.error("Page load or selector timeout during ATS application.")
                raise RuntimeError("ATS automation timed out.")
            finally:
                browser.close()

    @staticmethod
    def _fill_field(page, selectors: list[str], value: str):
        for selector in selectors:
            loc = page.locator(selector).first
            if loc.is_visible():
                loc.fill(value)
                return

    @staticmethod
    def _upload_file(page, selectors: list[str], file_path: str):
        for selector in selectors:
            loc = page.locator(selector).first
            if loc.is_visible():
                loc.set_input_files(file_path)
                return