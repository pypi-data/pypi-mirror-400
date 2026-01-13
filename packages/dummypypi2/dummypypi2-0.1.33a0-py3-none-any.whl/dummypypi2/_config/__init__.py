"""This is the module for global configuration of DummyPyPi2. Do not import this module directly, unless you know what you are doing."""

from . import algo

# Export variables by reference to maintain global state
def __getattr__(name: str) -> float:
    if name == 'RTOL':
        return algo.RTOL
    elif name == 'ATOL':
        return algo.ATOL
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")