from __future__ import annotations
from typing import Literal, Any

RTOL: float = 1E-5
ATOL: float = 1E-8

class _NumericalToleranceBase:
    """Base class with shared numerical tolerance setting functionality"""
    
    def _set_tolerance(self, *, rtol: float | None = None, atol: float | None = None) -> None:
        """Set global numerical tolerance values"""
        global RTOL, ATOL
        if rtol is not None:
            RTOL = rtol
        if atol is not None:
            ATOL = atol
    
    def _save_current_tolerance(self) -> tuple[float, float]:
        """Save current numerical tolerance values for restoration"""
        return RTOL, ATOL

class NumericalToleranceContextManager(_NumericalToleranceBase):
    """Context manager for temporarily setting numerical tolerance values.
    
    Call signature: (*, rtol=None, atol=None) -> NumericalToleranceContextManager
    
    Parameters
    ----------
    rtol : float or None, optional
        Relative tolerance value to use within the context.
        If None, the current rtol is unchanged within the context.
    atol : float or None, optional
        Absolute tolerance value to use within the context.
        If None, the current atol is unchanged within the context.
        
    Examples
    --------
    >>> with algo_options(rtol=1E-6, atol=1E-10):
    ...     # Code here uses the specified tolerances
    ...     pass
    >>> # Tolerances are automatically restored after the context
    """
    
    def __call__(self, *, rtol: float | None = None, atol: float | None = None) -> NumericalToleranceContextManager:
        """Configure tolerance values for context manager use"""
        self._rtol = rtol
        self._atol = atol
        return self

    def __enter__(self) -> NumericalToleranceContextManager:
        """Enter context: save current values and set new ones"""
        self._prev_rtol, self._prev_atol = self._save_current_tolerance()
        self._set_tolerance(rtol=self._rtol, atol=self._atol)
        return self

    def __exit__(self, *_: Any) -> None:
        """Exit context: restore previous numerical tolerance values"""
        global RTOL, ATOL
        RTOL, ATOL = self._prev_rtol, self._prev_atol

class NumericalToleranceSetter(_NumericalToleranceBase):
    """Global setter for numerical tolerance values.
    
    Call signature: (shortcut=None, *, rtol=None, atol=None) -> None
    
    Parameters
    ----------
    shortcut : {'default'} or None, optional
        Shortcut to set predefined tolerance values:
        - 'default': Sets rtol=1E-5, atol=1E-8
        If None, custom tolerances can be set via rtol/atol parameters.
    rtol : float or None, optional
        Relative tolerance value. If None, the current rtol is unchanged.
    atol : float or None, optional
        Absolute tolerance value. If None, the current atol is unchanged.
        
    Examples
    --------
    >>> set_algo_options('default')  # Set to default values
    >>> set_algo_options(rtol=1E-6, atol=1E-10)  # Set custom values
    >>> set_algo_options(rtol=1E-4)  # Only change rtol
    
    """
    
    def __call__(self, shortcut: Literal['default'] | None = None, *_: Any, rtol: float | None = None, atol: float | None = None) -> None:
        """Set global numerical tolerance values permanently"""
        if shortcut is None:
            # Only set custom tolerances
            self._set_tolerance(rtol=rtol, atol=atol)
        elif not isinstance(shortcut, str):
            raise ValueError("'set_algo_options' takes either no positional arguments or a single string argument 'default'. To set custom tolerances, use keyword arguments 'rtol' and/or 'atol'.")
        elif shortcut == 'default':
            # Set defaults first, then apply any custom overrides
            self._set_tolerance(rtol=1E-5, atol=1E-8)
            if rtol is not None or atol is not None:
                self._set_tolerance(rtol=rtol, atol=atol)

_algo_options_setter = NumericalToleranceSetter()

def set_algo_options(shortcut: Literal['default'] | None = None, /, *, rtol: float | None = None, atol: float | None = None) -> None:
    """Set global numerical tolerance values permanently.

    Parameters
    ----------
    shortcut : {'default'} or None, optional
        Shortcut to set predefined tolerance values:
        - 'default': Sets rtol=1E-5, atol=1E-8
        If None, custom tolerances can be set via rtol/atol parameters.
    rtol : float or None, optional
        Relative tolerance value. If None, the current rtol is unchanged.
    atol : float or None, optional  
        Absolute tolerance value. If None, the current atol is unchanged.

    Examples
    --------
    >>> set_algo_options('default')  # Set to default values
    >>> set_algo_options(rtol=1E-6, atol=1E-10)  # Set custom values
    >>> set_algo_options(rtol=1E-4)  # Only change rtol
    
    """
    return _algo_options_setter(shortcut, rtol=rtol, atol=atol)

_tolerance_context_manager = NumericalToleranceContextManager()

def algo_options(*, rtol: float | None = None, atol: float | None = None) -> NumericalToleranceContextManager:
    """Context manager for temporarily setting numerical tolerance values.

    Parameters
    ----------
    rtol : float or None, optional
        Relative tolerance value to use within the context.
        If None, the current rtol is unchanged within the context.
    atol : float or None, optional
        Absolute tolerance value to use within the context.
        If None, the current atol is unchanged within the context.
        
    Returns
    -------
    NumericalToleranceContextManager
        Context manager that temporarily sets the specified tolerances.

    Examples
    --------
    >>> with algo_options(rtol=1E-6, atol=1E-10):
    ...     # Code here uses the specified tolerances
    ...     pass
    >>> # Tolerances are automatically restored after the context
    
    >>> with algo_options(rtol=1E-4):
    ...     # Only rtol is temporarily changed
    ...     pass
    
    """
    return _tolerance_context_manager(rtol=rtol, atol=atol)