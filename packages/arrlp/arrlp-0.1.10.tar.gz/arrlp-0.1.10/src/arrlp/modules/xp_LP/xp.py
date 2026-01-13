#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-13
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : xp

"""
Use as a decorator for hybrid function numpy/cupy (CPU/GPU), inside the function, "xp" will correspond to np/cp.
"""



# %% Libraries
import functools
import numpy as np
try:
    import cupy as cp
except ImportError:
    cp = None



# %% Function
def xp(default=None) :
    '''
    Use as a decorator for hybrid function numpy/cupy (CPU/GPU), inside the function, "xp" will correspond to np/cp.
    
    Parameters
    ----------
    default : bool
        Sets default behavior, if True cuda will be used by default if available.

    Returns
    -------
    wrapper : function
        function wrapper where xp is numpy/cupy.

    Raises
    ------
    ImportError
        If cuda is asked but unavailable.

    Examples
    --------
    >>> from arrlp import xp
    >>> import numpy as np
    ...
    >>> @xp() # Decorator
    ... def sqrt_xp_function(array) :
    ...     arr = xp.asarray(array) # convert to array
    ...     return xp.sqrt(arr) # xp is numpy / cupy depending on what is available / default value
    >>> myarray = np.arange(20)
    >>> mysqrt = sqrt_xp_function(myarray) # default behavior
    >>> mysqrt = sqrt_xp_function(myarray, cuda=True) # Force cupy
    >>> mysqrt = sqrt_xp_function(myarray, cuda=False) # Force numpy
    '''

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, cuda=None, **kwargs):

            # Chosing xp
            if cuda is not None :
                if cuda and cp is None :
                    raise ImportError('Cupy is not available for xp function')
                _xp = cp if cuda else np
            else :
                if cp is None :
                    _xp = np
                else :
                    if default is None :
                        _xp = cp
                    else :
                        _xp = cp if default else np

            # Apply function with xp
            func_globals = func.__globals__
            old_xp = func_globals.get("xp", None)
            func_globals["xp"] = _xp
            try:
                return func(*args, **kwargs)
            finally:
                if old_xp is None:
                    del func_globals["xp"]
                else:
                    func_globals["xp"] = old_xp

        return wrapper
    return decorator




# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)