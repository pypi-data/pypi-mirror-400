from abc import ABC, abstractmethod


# TODO: I have 'yta_math.rate_functions' and should be used
class TimeFunction(ABC):
    """
    *Abstract class*
    """

    @abstractmethod
    def get_value_at(
        self,
        t: float
    ):
        """
        Get the value of the function at the `t` time
        moment provided.
        """
        pass

class ConstantTimeFunction(TimeFunction):
    """
    A time function in which the value is always constant,
    the same.
    """

    def __init__(
        self,
        value: float
    ):
        self.value: float = value

    def get_value_at(
        self,
        t: float
    ):
        return self.value
    
class LinearTimeFunction(TimeFunction):
    """
    A time function in which the value goes from the `v0`
    value to the `v1` value in the time lapse from `t0`
    to `t1`.
    """

    def __init__(
        self,
        t0: float,
        t1: float,
        v0: float,
        v1: float
    ):
        self.t0: float = t0
        self.t1: float = t1
        self.v0: float = v0
        self.v1: float = v1

    def get_value_at(
        self,
        t: float
    ):
        # TODO: The `t` should not be out of the limits
        if t <= self.t0:
            return self.v0
        
        if t >= self.t1:
            return self.v1
        
        k = (t - self.t0) / (self.t1 - self.t0)

        return self.v0 + k * (self.v1 - self.v0)