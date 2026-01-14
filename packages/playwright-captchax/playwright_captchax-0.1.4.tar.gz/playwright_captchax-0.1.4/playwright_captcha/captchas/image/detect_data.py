import logging
from typing import Union

from playwright.async_api import Page, Frame, ElementHandle

logger = logging.getLogger(__name__)


async def detect_image_data(queryable: Union[Page, Frame, ElementHandle], **kwargs) -> dict:
    """
    Detect the data for image captcha (e.g., image source, input field)

    :param queryable: The Playwright Page, Frame, or ElementHandle to search for the captcha data
    :param kwargs: Additional parameters (can include 'image_selector', 'input_selector')

    :return: A dictionary containing the detected captcha data needed for solving
    """

    logger.debug('Detecting image captcha data...')

    data = {}

    # Get custom selectors from kwargs or use defaults
    image_selector = kwargs.get('image_selector', 'img[src*="captcha"], img[alt*="captcha"], img.captcha')
    input_selector = kwargs.get('input_selector', 'input[name*="captcha"], input[id*="captcha"], input.captcha')

    # Try to find the captcha image
    try:
        image_element = await queryable.query_selector(image_selector)
        if image_element:
            # Get the image source (could be a URL or base64)
            image_src = await image_element.get_attribute('src')
            if image_src:
                data['file'] = image_src
                logger.debug(f'Found image captcha source: {image_src[:100]}...')
    except Exception as e:
        logger.warning(f'Failed to detect image element: {e}')

    # Try to find the input field for the captcha answer
    # Only set the selector if we actually find the element
    try:
        input_element = await queryable.query_selector(input_selector)
        if input_element:
            # Get input field properties
            input_name = await input_element.get_attribute('name')
            input_id = await input_element.get_attribute('id')

            # Store the selector for applying the captcha
            if input_name:
                data['_apply_captcha_input_selector'] = f'input[name="{input_name}"]'
            elif input_id:
                data['_apply_captcha_input_selector'] = f'input[id="{input_id}"]'
            else:
                data['_apply_captcha_input_selector'] = input_selector

            logger.debug(f'Found input field: {data.get("_apply_captcha_input_selector")}')
        else:
            logger.debug(f'No input field found with default selector: {input_selector}')
            # Don't set any selector if not found - let the caller provide it explicitly
    except Exception as e:
        logger.warning(f'Failed to detect input element: {e}')

    logger.debug(f'Detected image captcha data: {data}')

    return data
