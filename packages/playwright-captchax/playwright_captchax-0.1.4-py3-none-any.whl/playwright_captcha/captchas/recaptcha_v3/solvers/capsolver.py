import logging

from playwright_captcha.solvers.api.capsolver.capsolver.async_solver import AsyncCapSolver
from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_recaptcha_v3_capsolver(async_capsolver_client: AsyncCapSolver, **kwargs) -> dict:
    """
    Solve Recaptcha V3 captcha using CapSolver service.

    :param async_capsolver_client: Instance of AsyncCapSolver client
    :param kwargs: Parameters for the CapSolver API call, e.g. 'sitekey'

    :return: Result of the captcha solving
    """

    logger.debug('Solving Recaptcha V3 captcha using CapSolver...')

    validate_required_params(['sitekey', 'url'], kwargs)

    kwargs['version'] = 'v3'
    result = await async_capsolver_client.recaptcha(
        **kwargs
    )

    logger.debug(f'Solved Recaptcha V3: {result}')

    return result
