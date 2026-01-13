#%%
import pytest
import numpy as np
from np_vmd.tdof_MCK import TDOF_modal
from np_vmd.tdof_response_inman import MDOFFreeResponseI

def test_mdof_free_resp_modal_set_iv():
    # examples inman 4.3.2
    m1,m2  = 9,1
    k1=24
    k2=3
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]))
    # create free response object
    r_free = MDOFFreeResponseI(mdof_sys=tmck)
    r_free.set_iv(x0s = np.array([[1,0]]).T, dx0s = np.array([[0,0]]).T)
    r_free._set_rfs_hom()
    ts = np.linspace(0, 5,10)
    r1 = 3/np.sqrt(2)*np.cos(2*ts)
    r2 = 3/np.sqrt(2)*np.cos(np.sqrt(2)*ts)
    np.testing.assert_almost_equal(r_free.rfs_h[0](ts),r1 ,4)
    np.testing.assert_almost_equal(r_free.rfs_h[1](ts),r2 ,4)

def test_mdof_free_resp_set_rfs_hom():
    # examples inman 4.3.2
    m1,m2  = 9,1
    k1=24
    k2=3
    # Create system
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]))
    # create free response object
    r_free = MDOFFreeResponseI(mdof_sys=tmck)
    r_free.set_iv(x0s = np.array([[1,0]]).T, dx0s = np.array([[0,0]]).T)
    r_free._set_rfs_hom()
    # 
    ts = np.linspace(0, 5,10)
    r1 = 3/np.sqrt(2)*np.cos(2*ts)
    r2 = 3/np.sqrt(2)*np.cos(np.sqrt(2)*ts)
    np.testing.assert_almost_equal(r_free.rfs_h[0](ts),r1 ,4)
    np.testing.assert_almost_equal(r_free.rfs_h[1](ts),r2 ,4)

# %%
def test_mdof_free_resp_calc_xs():
    # examples inman 4.3.2
    m1,m2  = 9,1
    k1=24
    k2=3
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]))
    # create free response object
    r_free = MDOFFreeResponseI(mdof_sys=tmck)
    r_free.set_iv(x0s = np.array([[1,0]]).T, dx0s = np.array([[0,0]]).T)
    # tests
    ts = np.linspace(0, 5,10)
    xs1 = 0.5*(np.cos(np.sqrt(2)*ts) + np.cos(2*ts))
    xs2 =  1.5*(np.cos(np.sqrt(2)*ts) - np.cos(2*ts))
    xs = r_free.calc_x_hom_response(ts)
    np.testing.assert_almost_equal(xs[0,:],xs1 ,4)
    np.testing.assert_almost_equal(xs[1,:],xs2 ,4)

# %%
def test_mdof_free_resp_inman_4_5_1_calc_xs():
    '''This is for the calculation of the xs values

     # numerical value from Inman 4th ed. Engineering Vibration, example: 4.5.1. 
    '''
    m1,m2  = 9,1
    k1=24
    k2=3
    c1 = 0
    c2 = 0
    F0=3
    w0=2
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]), C= np.array([[c1+c2,-c2],[-c2,c2]]))
    tmck.update_damping(  np.array([0.1, 0.05]))
    # create free response object
    r_free = MDOFFreeResponseI(mdof_sys=tmck)
    r_free.set_iv(x0s = np.array([[1, 0]]).T, dx0s = np.array([[0,0]]).T)
    np.testing.assert_almost_equal(r_free.r0s, 3/np.sqrt(2)*np.array([[1,1]]).T,4)
    
    # tests
    ts = np.linspace(0, 1,10)
    # # homogeneous (transient) solutions
    xhs1 = 0.5006*np.exp(-0.0706*ts)*np.sin(1.4124*ts+1.52) + \
            0.5025*np.exp(-0.2*ts)*np.sin(1.9900*ts+1.47)
    xhs2 =  1.5019*np.exp(-0.0706*ts)*np.sin(1.4124*ts+1.52) - \
            1.5076*np.exp(-0.2*ts)*np.sin(1.9900*ts+1.47)

    xs = r_free.calc_x_hom_response(ts)
    np.testing.assert_almost_equal(xs[0,:],xhs1, 3)
    np.testing.assert_almost_equal(xs[1,:],xhs2, 3)

def test_mdof_free_resp_inman_4_5_1_calc_xs_alternative():
    '''This test the validity of the calculation for TDOF_modal.calc_C_from_Z()

    This continues from where the previous test left off
    '''
    m1,m2  = 9,1
    k1=24
    k2=3
    F0=3
    w0=2
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]), C= np.zeros((2,2)))
    tmck.update_damping(  np.array([0.1, 0.05]))
    
    tmckn = tmck.calc_C_from_Z(tmck.zs) # new mdof with update damping values
    np.testing.assert_almost_equal(tmckn.zs, np.array([0.1, 0.05]),4)
    
    # create free response object with new mdof
    r_free = MDOFFreeResponseI(mdof_sys=tmckn)
    # tmck.update_damping(  np.array([0.1, 0.05]))
    r_free.set_iv(x0s = np.array([[1, 0]]).T, dx0s = np.array([[0,0]]).T)
    np.testing.assert_almost_equal(r_free.r0s, 3/np.sqrt(2)*np.array([[1,1]]).T,4)
    
    ts = np.linspace(0, 1,10)
    # # homogeneous (transient) solutions
    xhs1 = 0.5006*np.exp(-0.0706*ts)*np.sin(1.4124*ts+1.52) + \
            0.5025*np.exp(-0.2*ts)*np.sin(1.9900*ts+1.47)
    xhs2 =  1.5019*np.exp(-0.0706*ts)*np.sin(1.4124*ts+1.52) - \
            1.5076*np.exp(-0.2*ts)*np.sin(1.9900*ts+1.47)

    xs = r_free.calc_x_hom_response(ts)
    np.testing.assert_almost_equal(xs[0,:],xhs1, 3)
    np.testing.assert_almost_equal(xs[1,:],xhs2, 3)