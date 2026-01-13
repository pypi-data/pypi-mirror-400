import random


def hard_round(value: float, decimals: int = 2) -> float:
    """
    Rounds a float to a specified number of decimal places with hard rounding.

    Required Arguments:

    - value (float): The float value to be rounded.

    Optional Arguments:

    - decimals (int): The number of decimal places to round to.
        - Default: 2

    Returns:

    - float: The rounded float value.
    """
    factor = 10**decimals
    return round(value * factor) / factor


class NormalGenerator:
    def __init__(self, seed=None):
        self.random = random.Random(seed)

    def __call__(self, mean, sigma, min=None, precision=6):
        output = self.random.gauss(mean, sigma)
        if min is not None:
            output = max(min, output)
        return round(output, precision)
