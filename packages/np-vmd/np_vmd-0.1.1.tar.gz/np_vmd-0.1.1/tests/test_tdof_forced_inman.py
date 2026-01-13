# TODO: this is not completed 

#%%
import pytest
import numpy as np
from np_vmd.tdof_MCK import TDOF_modal
from np_vmd.tdof_response_inman import MDOFGenericResponseI

@pytest.fixture
def tmck()->TDOF_modal:
    '''pytest fixture for the forced response
    '''
    m1,m2  = 9,1
    k1=24
    k2=3
    c1 = 2.4
    c2 = 0.3 
    tmck = TDOF_modal(
        np.array([[m1,0],[0,m2]]), 
        K=np.array([[k1+k2,-k2],[-k2,k2]]), 
        C= np.array([[c1+c2,-c2],[-c2,c2]]))
   
    return tmck

def test_modal_inman_4_6_1(tmck):
    # examples 4.6.1.
    ''' With damping and forced
    '''
    F0=3
    w0=2
    # ================================ system related =====================================
    np.testing.assert_equal(tmck.Ktilde, np.array([[3,-1],[-1,3]]))
    np.testing.assert_almost_equal(tmck.Ctilde, np.array([[0.3,-.1],[-.1,.3]]), 4)
    #eigenvalues
    np.testing.assert_almost_equal(tmck.ls, np.array([4,2]),4)
    #eigenfrequencies
    np.testing.assert_almost_equal(tmck.wns, np.array([2, 1.41421]),4) 
    # calculate decoupled cs
    np.testing.assert_almost_equal(tmck._calc_C_princ_coord(), np.array([[0.4,0],[0,0.2]]), 4)
    # calculate decoupled damping factors
    np.testing.assert_almost_equal(np.diag(tmck._calc_C_princ_coord())/(2*tmck.wns), np.array([0.1,0.0707]), 4)
    np.testing.assert_almost_equal(tmck.zs, np.array([0.1,0.0707]), 4)
    np.testing.assert_almost_equal(tmck.wds, np.array([1.9899,1.4106]), 3)

    #eigenvectors
    np.testing.assert_almost_equal(tmck.vs, np.array([[0.70710678 ,0.70710678 ],[-0.70710678 , 0.70710678 ]]),4)
    #eigenmodes
    np.testing.assert_almost_equal(tmck.us, np.array([[1,1],[-0.333333, 0.3333333]]),4)
    np.testing.assert_almost_equal(tmck.Lambda_mat, np.array([[4, 0], [0, 2]]),4)
    np.testing.assert_almost_equal(tmck.Lambda_mat, np.diag([4,  2]),4)
    
    # ================== FOrce excitation ============
    # print(tmck.Linv)
    # calculate B tilde
    r_generic = MDOFGenericResponseI(tmck)
    r_generic.set_excitation(B=np.array([[0,0],[0,1]]),F=[0,lambda t:3*np.cos(2*t)])
    np.testing.assert_almost_equal(r_generic.B_tilde.dot(np.array([[1,1]]).T), np.sqrt(2)/2*np.array([[-1,1]]).T, 4)
    # TODO : Complete test 

def test_INCOMPLETE_modal_inman_4_6_1_calc_xs(tmck):
    '''This is for the calculation of the xs values

    This continues from where the previous test left of
    '''
    F0=3
    w0=2


    # ================== FOrce excitation ============
    # calculate B tilde
    # tmck.set_excitation(B=np.array([[0,0],[0,1]]),F=[0,lambda t:3*np.cos(2*t)])

    # # TODO: complete test
    # tmck.set_iv(x0s = np.array([[0, 0]]).T, dx0s = np.array([[0,0]]).T)
    # np.testing.assert_almost_equal(tmck.r0s, np.array([[0,0]]).T,4)

    # # The following x_repsonse does not work. Might be due to rounding error. 
    # ts = np.linspace(0, 1,10)
    # rs1 = 1.040*np.cos(2*ts+0.1974) # r2p in the book
    # rs2 = 2.6516*np.sin(2*ts)  # r1p in the book
    # # steady state solutions
    # xss1 = 0.2451*np.cos(2*ts-2.9442) - 0.6249*np.sin(2*ts)
    # xss2 = 0.7354*np.sin(2*ts-2.9442) - 0.8749*np.sin(2*ts)

    # xs = tmck.calc_x_response_forced_ss(ts)
    # np.testing.assert_almost_equal(xs[0,:],xss1, 3)
    # np.testing.assert_almost_equal(xs[1,:],xss2, 4)

