import logging

from playwright_captcha.solvers.api.capsolver.capsolver.async_solver import AsyncCapSolver
from playwright_captcha.utils.validators import validate_required_params

logger = logging.getLogger(__name__)


async def solve_image_capsolver(async_capsolver_client: AsyncCapSolver, **kwargs) -> dict:
    """
    Solve image/normal captcha using CapSolver service

    :param async_capsolver_client: Instance of AsyncCapSolver client
    :param kwargs: Parameters for the CapSolver API call, including 'file' (required)
                   Optional params: module, score, case

    :return: Result of the captcha solving
    """

    logger.debug('Solving image captcha using CapSolver...')

    validate_required_params(['file'], kwargs)

    result = await async_capsolver_client.normal(**kwargs)

    logger.debug(f'Solved image captcha: {result}')

    return result
