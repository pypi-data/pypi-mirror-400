"""Delay and smoothing functions for World3 model"""

from typing import Literal
import numpy as np
import numpy.typing as npt
from scipy.integrate import odeint


def _func_delay1(out_: float, t_: float, in_: float, del_: float) -> float:
    """Computes derivative for 1st order delay (used in odeint)"""
    return (in_ - out_) / del_


def _func_delay3(
    out_: npt.NDArray[np.float64], t_: float, in_: float, del_: float
) -> npt.NDArray[np.float64]:
    """Computes derivative for 3rd order delay (used in odeint)"""
    dout_ = np.zeros(3)
    dout_[0] = in_ - out_[0]
    dout_[1] = out_[0] - out_[1]
    dout_[2] = out_[1] - out_[2]
    return dout_ * 3 / del_


class Smooth:
    """
    1st order delay information function for smoothing (DLINF1 in Dynamo).

    Computes smoothed output from input vector with exponential smoothing.
    Used for modeling information delays and perception lags.

    Args:
        in_arr: Input vector to be smoothed
        dt: Time step
        t: Time vector
        method: Integration method ("euler" or "odeint")

    Example:
        >>> import numpy as np
        >>> t = np.arange(0, 100, 1)
        >>> in_arr = np.ones(100) * 5.0
        >>> smooth = Smooth(in_arr, dt=1.0, t=t)
        >>> result = smooth(k=10, delay=3.0, init_val=1.0)
    """

    def __init__(
        self,
        in_arr: npt.NDArray[np.float64],
        dt: float,
        t: npt.NDArray[np.float64],
        method: Literal["euler", "odeint"] = "euler",
    ):
        self.dt = dt
        self.out_arr = np.zeros(t.size)
        self.in_arr = in_arr
        self.method = method

    def __call__(self, k: int, delay: float, init_val: float) -> float:
        """
        Compute smoothed value at time step k.

        Args:
            k: Current time step index
            delay: Delay time constant (higher = more smoothing)
            init_val: Initial value for the smoothed output

        Returns:
            Smoothed value at step k
        """
        if k == 0:
            self.out_arr[k] = init_val
        else:
            if self.method == "odeint":
                res = odeint(
                    _func_delay1,
                    self.out_arr[k - 1],
                    [0, self.dt],
                    args=(self.in_arr[k - 1], delay),
                )
                self.out_arr[k] = res[1, 0]
            elif self.method == "euler":
                dout = (self.in_arr[k - 1] - self.out_arr[k - 1]) * self.dt / delay
                self.out_arr[k] = self.out_arr[k - 1] + dout

        return self.out_arr[k]


# Alias for compatibility
DlInf1 = Smooth


class Delay3:
    """
    3rd order delay function.

    Provides a more realistic delay with distributed lag compared to
    1st order delay. The delay is distributed across three stages,
    creating a bell-shaped impulse response.

    Args:
        in_arr: Input vector to be delayed
        dt: Time step
        t: Time vector
        method: Integration method ("euler" or "odeint")

    Example:
        >>> import numpy as np
        >>> t = np.arange(0, 100, 1)
        >>> in_arr = np.ones(100) * 5.0
        >>> delay3 = Delay3(in_arr, dt=1.0, t=t)
        >>> result = delay3(k=10, delay=5.0)
    """

    def __init__(
        self,
        in_arr: npt.NDArray[np.float64],
        dt: float,
        t: npt.NDArray[np.float64],
        method: Literal["euler", "odeint"] = "euler",
    ):
        self.dt = dt
        self.out_arr = np.zeros((t.size, 3))
        self.in_arr = in_arr
        self.method = method

        if self.method == "euler":
            self.A_norm = np.array([[-1.0, 0.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, -1.0]])
            self.B_norm = np.array([1.0, 0.0, 0.0])

    def _init_out_arr(self, delay: float) -> None:
        """Initialize output array at t=0"""
        self.out_arr[0, :] = self.in_arr[0] * 3 / delay

    def __call__(self, k: int, delay: float) -> float:
        """
        Compute delayed value at time step k.

        Args:
            k: Current time step index
            delay: Delay time constant

        Returns:
            Delayed value at step k (output from 3rd stage)
        """
        if k == 0:
            self._init_out_arr(delay)
        else:
            if self.method == "odeint":
                res = odeint(
                    _func_delay3,
                    self.out_arr[k - 1, :],
                    [0, self.dt],
                    args=(self.in_arr[k - 1], delay),
                )
                self.out_arr[k, :] = res[1, :]
            elif self.method == "euler":
                # Optimized: inline matrix multiplication to avoid overhead
                prev = self.out_arr[k - 1]
                factor = self.dt * 3 / delay
                in_val = self.in_arr[k - 1]
                # dout = A_norm @ prev + B_norm * in_val, expanded inline
                d0 = (-prev[0] + in_val) * factor
                d1 = (prev[0] - prev[1]) * factor
                d2 = (prev[1] - prev[2]) * factor
                self.out_arr[k, 0] = prev[0] + d0
                self.out_arr[k, 1] = prev[1] + d1
                self.out_arr[k, 2] = prev[2] + d2

        return self.out_arr[k, 2]


class Dlinf3(Delay3):
    """
    3rd order delay information function for smoothing.

    Similar to Delay3 but with initialization that assumes the input
    has been constant at its initial value. This is more appropriate
    for information delays than material delays.

    The key difference from Delay3 is the initialization: instead of
    scaling by 3/delay, all stages are initialized to the input value.

    Args:
        in_arr: Input vector to be smoothed
        dt: Time step
        t: Time vector
        method: Integration method ("euler" or "odeint")

    Example:
        >>> import numpy as np
        >>> t = np.arange(0, 100, 1)
        >>> in_arr = np.ones(100) * 5.0
        >>> dlinf3 = Dlinf3(in_arr, dt=1.0, t=t)
        >>> result = dlinf3(k=10, delay=5.0)
    """

    def _init_out_arr(self, delay: float) -> None:
        """Initialize output array assuming steady state at t=0"""
        self.out_arr[0, :] = self.in_arr[0]
