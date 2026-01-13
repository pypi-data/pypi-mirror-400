#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-13
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : arrLP
# Module        : xp

"""
This file allows to test xp

xp : Use as a decorator for hybrid function numpy/cupy (CPU/GPU), inside the function, "xp" will correspond to np/cp.
"""



# %% Libraries
from corelp import print, debug
import pytest
import numpy as np
try:
    import cupy as cp
except ImportError:
    cp = None
from arrlp import xp
debug_folder = debug(__file__)



# %% Function test
def test_numpy() :
    '''
    Test np function
    '''
    
    @xp()
    def default_none() :
        return xp
    @xp(True)
    def default_true() :
        return xp
    @xp(False)
    def default_false() :
        return xp
    
    assert np == default_true(cuda=False)
    assert np == default_false(cuda=False)
    assert np == default_none(cuda=False)
    assert np == default_false()
    if cp is None :
        assert np == default_none()
    


# %% Function test
def test_cupy() :
    '''
    Test cp function
    '''
    
    if cp is None :
        return None

    print('Cupy installed and can be tested on xp')
    @xp()
    def default_none() :
        return xp
    @xp(True)
    def default_true() :
        return xp
    @xp(False)
    def default_false() :
        return xp
    
    assert cp == default_true(cuda=True)
    assert cp == default_false(cuda=True)
    assert cp == default_none(cuda=True)
    assert cp == default_true()
    assert np == default_none()
    




# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)