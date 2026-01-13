
import pytest
from np_vmd.sdof_funcs import SDOF_system
import numpy as np


def test_sdof_underdamped():
    """ the aim of this test is to check the SDOF system response functions based on 
    known values from different examples
    """
    ss = SDOF_system.from_wn_mz(m = 1, wn=1, zeta= 0.4 )
    x0 = 2
    xdot0=-3
    fdic = ss.free_response_at_t_funcs(x0=x0, v0=xdot0)
    t= 1

    assert ss.wn == pytest.approx(1, rel=1e-3)
    assert ss.zeta == pytest.approx(0.4, rel=1e-3)
    assert ss.wd == pytest.approx(0.916515, rel=1e-4)
    assert ss.zeta*ss.wn == pytest.approx(0.4,1e-2)
    
    assert fdic['x'](0)== pytest.approx(2,rel=1e-3)   
    assert fdic['x'](t)== pytest.approx(-0.4608,rel=1e-3)

    assert fdic['v'](0)== pytest.approx(-3,rel=1e-3)   
    assert fdic['v'](t)== pytest.approx(-1.6881,rel=1e-3)


def test_sdof_underdamped_gowda():
    """ the aim of this test is to check the SDOF system response functions based on 
    known values from gowda example 3.5
    """
    ss = SDOF_system(m = 20, c=150, k=10000)
    x0 = 0
    xdot0= .1
    fdic = ss.free_response_at_t_funcs(x0=x0, v0=xdot0)
    t= 1
   
    assert ss.wn == pytest.approx(22.3607, rel=1e-3)
    assert ss.zeta == pytest.approx(0.1677, rel=1e-3)
    assert ss.wd == pytest.approx(22.044, rel=1e-4)
    assert ss.zeta*ss.wn == pytest.approx(3.75,1e-2)
    assert ss.amplitude(x0=x0, v0=xdot0) == pytest.approx(4.5366e-3,rel=1e-4)
    assert ss.phase_sin(x0=x0, v0=xdot0) == pytest.approx(0,rel=1e-4)
    # assert that fdic['x'](t) is close to -0.49960611560456053
    assert  fdic['x'](0) == pytest.approx(0,rel= 1e-4)
    assert  fdic['x'](t) == pytest.approx(-5.6348e-6,rel= 1e-3)

    assert  fdic['v'](0) == pytest.approx(.1,rel= 1e-4), "Velocity at the start of the simulation is not correct"
    assert  fdic['v'](t) == pytest.approx(-0.002327361,rel= 1e-4), "Velocity at t=1[s] is not correct"


    
def test_sdof_critically_damped():
    """ the aim of this test is to check the  response functions
    of CRITICALLY DAMPED SDOF system is correct 
    """
    ss = SDOF_system(m = 1, c=2, k=1)
    x0 = 0.2
    xdot0= -.3
    fdic = ss.free_response_at_t_funcs(x0=x0, v0=xdot0)
    t= 1
   
    assert ss.wn == pytest.approx(1, rel=1e-3)
    assert ss.zeta == pytest.approx(1, rel=1e-3)
    # assert that fdic['x'](t) is close to -0.49960611560456053
    assert  fdic['x'](0) == pytest.approx(0.2,rel= 1e-6)
    assert  fdic['x'](t) == pytest.approx(0.0367879,rel= 1e-5)

    assert  fdic['v'](0) == pytest.approx(-0.3,rel= 1e-4)
    assert  fdic['v'](t) == pytest.approx(-0.0735759,rel= 1e-4)

    
     
def test_sdof_over_damped():
    """ the aim of this test is to check the  response functions
    of OVER-DAMPED SDOF system is correct 
    """
    ss = SDOF_system(m = 1, c=5, k=1)
    x0 = 0.2
    xdot0= -.3
    fdic = ss.free_response_at_t_funcs(x0=x0, v0=xdot0)
    t= 1
   
    assert ss.wn == pytest.approx(1, rel=1e-3)
    assert ss.zeta == pytest.approx(2.5, rel=1e-3)
    # assert that fdic['x'](t) is close to -0.49960611560456053
    assert  fdic['x'](0) == pytest.approx(0.2,rel= 1e-6)
    assert  fdic['x'](t) == pytest.approx(0.1170531,rel= 1e-5)

    #TODO need to perform derivations and obtain the solutions for over-damped systems
    assert  fdic['v'](0) == pytest.approx(-0.3,rel= 1e-4)
    assert  fdic['v'](t) == pytest.approx(-0.0265744,rel= 1e-4)
