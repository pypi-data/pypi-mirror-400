# pygbm/base_pygbm.py

class BaseGBM:
    """
    Base class for Geometric Brownian Motion (GBM) models.

    This class stores the common parameters defining a GBM model.
    It is intended to be subclassed by concrete simulators that
    implement specific simulation or visualisation methods.

    Attributes
    ----------
    y0 : float
        Initial value Y(0) of the stochastic process.
    mu : float
        Drift parameter controlling the average exponential growth rate.
    sigma : float
        Volatility parameter controlling the magnitude of random fluctuations.
    """

    def __init__(self, y0, mu, sigma):
        """
        Initialise the parameters of a Geometric Brownian Motion model.

        Parameters
        ----------
        y0 : float
            Initial value Y(0) of the process.
        mu : float
            Drift parameter controlling the average growth rate.
        sigma : float
            Volatility parameter controlling the strength of random fluctuations.
        """
        self.y0 = y0
        self.mu = mu
        self.sigma = sigma
