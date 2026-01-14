import logging

from playwright.async_api import Page

from playwright_captcha.utils.exceptions import CaptchaApplyingError

logger = logging.getLogger(__name__)


async def apply_image_captcha(page: Page, token: str, *args, **kwargs) -> None:
    """
    Apply the solved captcha text to the input field on the page

    :param page: Playwright Page containing the captcha
    :param token: The solved captcha text returned by the solving service
    :param kwargs: Additional parameters, including 'input_selector' to specify the input field

    :raises CaptchaApplyingError: If the captcha solution could not be applied
    """

    logger.debug("Attempting to apply image captcha solution...")

    # Get the input selector from kwargs (should be set by detect_data.py or passed explicitly)
    # Check for _apply_captcha_input_selector first (standard convention), then fall back to input_selector
    input_selector = kwargs.get('_apply_captcha_input_selector') or kwargs.get('input_selector', 'input[name*="captcha"], input[id*="captcha"], input.captcha')

    try:
        # Find the input field
        input_element = await page.query_selector(input_selector)

        if not input_element:
            raise CaptchaApplyingError(f"Could not find input field with selector: {input_selector}")

        # Clear any existing value and fill in the solved captcha text
        await input_element.fill('')
        await input_element.fill(token)

        logger.info(f"Successfully applied image captcha solution to {input_selector}")

    except Exception as e:
        logger.error(f"Failed to apply image captcha: {e}")
        raise CaptchaApplyingError(f"Failed to apply image captcha solution: {e}")
