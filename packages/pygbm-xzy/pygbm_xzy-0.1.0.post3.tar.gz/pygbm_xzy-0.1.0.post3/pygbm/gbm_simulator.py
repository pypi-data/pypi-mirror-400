# pygbm/gbm_simulator.py

import numpy as np
import matplotlib.pyplot as plt
from .base_gbm import BaseGBM


class GBMSimulator(BaseGBM):
    """
    Simulator for Geometric Brownian Motion (GBM).

    This class implements a concrete GBM model by extending the BaseGBM
    base class. It provides methods to simulate a single GBM path over
    a fixed time horizon and to visualise the resulting trajectory.

    Parameters
    ----------
    y0 : float
        Initial value Y(0) of the process.
    mu : float
        Drift parameter controlling the average growth rate.
    sigma : float
        Volatility parameter controlling the strength of random fluctuations.
    """

    def __init__(self, y0, mu, sigma):
        """
        Initialise the GBM simulator with model parameters.

        Parameters
        ----------
        y0 : float
            Initial value Y(0).
        mu : float
            Drift coefficient.
        sigma : float
            Volatility coefficient.
        """
        super().__init__(y0, mu, sigma)

    def simulate_path(self, T, N):
        """
        Simulate a single path of the Geometric Brownian Motion.

        The simulation is performed by discretising the time interval
        [0, T] into N equal steps and applying the exact GBM update
        formula on each step.

        Parameters
        ----------
        T : float
            Total time horizon of the simulation.
        N : int
            Number of discrete time steps.

        Returns
        -------
        t_values : numpy.ndarray
            Array of time points with shape (N + 1,).
        y_values : list of float
            Simulated GBM values corresponding to each time point.
        """
        dt = T / N
        t_values = np.linspace(0, T, N + 1)
        y_values = [self.y0]

        for _ in range(N):
            y_prev = y_values[-1]
            dB = np.random.normal(0, np.sqrt(dt))
            y_next = y_prev * np.exp(
                (self.mu - 0.5 * self.sigma ** 2) * dt
                + self.sigma * dB
            )
            y_values.append(y_next)

        return t_values, y_values

    def plot_path(self, t_values, y_values, output=None):
        """
        Plot a simulated GBM path.

        Parameters
        ----------
        t_values : array-like
            Time grid returned by `simulate_path`.
        y_values : array-like
            Simulated GBM values returned by `simulate_path`.
        output : str or None, optional
            If provided, the plot is saved to the specified file path.
            Otherwise, the plot is displayed on screen.
        """
        plt.plot(t_values, y_values, label="GBM Path")
        plt.xlabel("Time")
        plt.ylabel("Y(t)")
        plt.title("Simulated Geometric Brownian Motion Path")
        plt.legend()

        if output:
            plt.savefig(output)
        else:
            plt.show()
