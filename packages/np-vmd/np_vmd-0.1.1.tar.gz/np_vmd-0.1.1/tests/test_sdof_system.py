
import pytest
from np_vmd.sdof_funcs import SDOF_system
import numpy as np


def test_sdof_system():
    ss = SDOF_system(m = 1, k =4, c= 0.1 )
    assert(ss.m, 1) 
    assert(ss.k, 4)
    assert(ss.c, 0.1) 
    pytest.approx(ss.zeta, 0.1/(2*ss.m*ss.wn),abs=1e-4) 
    pytest.approx(ss.wd, ss.wn*np.sqrt(1-ss.zeta**2),abs=1e-4) 
    pytest.approx(ss.delta ,1.2825 ,abs=1e-4) # logaritmic decretemnt
        
    pytest.approx(ss.T,  3.1415, abs=1e-4) # period no damping
    pytest.approx(ss.Td, 3.1426, abs=1e-4) # damping period


def test_sdof_system_kelly3_6():
    ''' Kelly 3.6

    '''
    ss = SDOF_system(m = 4.6e-12, k =0.380, c= 4.93e-7 )
    assert(ss.m,  4.6e-12) 
    assert(ss.k, 0.380)
    assert(ss.c, 4.93e-7) 
    assert ss.wn == pytest.approx(2.874e5, rel= 1e-3)  
    assert ss.zeta == pytest.approx(0.18644, rel= 1e-3) 
    assert ss.wd == pytest.approx(2.8237e5, rel= 1e-3) 
    