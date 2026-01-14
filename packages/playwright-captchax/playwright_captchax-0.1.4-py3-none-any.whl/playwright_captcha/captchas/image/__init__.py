from playwright_captcha import BaseSolver, CaptchaType

from .apply import apply_image_captcha
from .detect_data import detect_image_data
from .solvers.capsolver import solve_image_capsolver
from .solvers.tencaptcha import solve_image_tencaptcha
from ...types.solvers import SolverType

# register solvers
BaseSolver.register_solver(SolverType.tencaptcha, CaptchaType.IMAGE, solve_image_tencaptcha)
BaseSolver.register_solver(SolverType.capsolver, CaptchaType.IMAGE, solve_image_capsolver)

# register detector
BaseSolver.register_detector(CaptchaType.IMAGE, detect_image_data)

# register appliers
BaseSolver.register_applier(CaptchaType.IMAGE, apply_image_captcha)
