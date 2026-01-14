import logging

from playwright_captcha.solvers.api.tencaptcha.tencaptcha.async_solver import AsyncTenCaptcha
from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_image_tencaptcha(async_ten_captcha_client: AsyncTenCaptcha, **kwargs) -> dict:
    """
    Solve image/normal captcha using 10Captcha service

    :param async_ten_captcha_client: Instance of AsyncTenCaptcha client
    :param kwargs: Parameters for the 10Captcha API call, including 'file' (required)
                   Optional params: phrase, regsense, numeric, calc, min_len, max_len, language, lang, module

    :return: Result of the captcha solving
    """

    logger.debug('Solving image captcha using 10Captcha...')

    validate_required_params(['file'], kwargs)

    result = await async_ten_captcha_client.normal(**kwargs)

    logger.debug(f'Solved image captcha: {result}')

    return result
