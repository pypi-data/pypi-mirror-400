import numpy as np
def cartesian_to_polar(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rho = np.sqrt(x*x + y*y)
    phi = np.arctan2(y, x)
    return rho, phi
