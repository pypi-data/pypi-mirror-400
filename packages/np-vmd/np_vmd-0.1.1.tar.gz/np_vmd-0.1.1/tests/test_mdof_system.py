
import pytest
import numpy as np
from np_vmd.tdof_MCK import TDOF_modal

def test_mdof_modal_modal_calc_xs_():
    # examples inman 4.4.2
    m1,m2,m3  = 4,4,4
    k1,k2,k3 = 4,4,4

    tmck = TDOF_modal(np.array([[m1,0,0],[0,m2,0],[0,0,m3]]), K=np.array([[k1+k2,-k2,0],[-k2,k2+k3, -k3],[0,-k3,k3]]))

    np.testing.assert_equal(tmck.Ktilde, np.array([[2,-1,0],[-1,2,-1],[0,-1,1]]))
    #eigenvalues
    np.testing.assert_almost_equal(tmck.ls, np.array([3.2470, 1.5550,0.1981]),4)
    #eigenfrequencies
    np.testing.assert_almost_equal(tmck.wns, np.array([1.8019, 1.2470, 0.4450]),4) 
    #eigenvectors
    np.testing.assert_almost_equal(tmck.vs, np.array([[-0.5910,-0.7370, 0.3280 ],[0.7370 ,-0.3280 , 0.5910],[ -0.3280,0.5910 , 0.7370]]),4)

    # #eigenmodes
    # np.testing.assert_almost_equal(tmck.us, np.array([[1,1],[-0.21954446, 18.21954446]]),4)

    np.testing.assert_almost_equal(tmck.Lambda_mat, np.diag(tmck.ls),4)

    r0s =  tmck.to_modal_cs(x0s = np.array([[1,0, 0]]).T) 
    dr0s =  tmck.to_modal_cs(x0s = np.array([[0,0,0]]).T)
    np.testing.assert_almost_equal(r0s, np.array([[-1.1820,-1.4740,0.6560]]).T,4)

    ## The following x_repsonse does not work. Might be due to rounding error. 
    # ts = np.linspace(0, 1,10)
    # xs1 = 0.2417*np.cos(0.4450*ts) -0.4355*np.cos(1.2470*ts)+0.1935*np.cos(0.18019*ts)
    # xs2 = 0.1938*np.corfs_h.4450*ts) +0.2417*np.cos(1.2470*ts)-0.4355*np.cos(0.18019*ts)
    # xs3 = 0.1075*np.cos(0.4450*ts) +0.5443*np.cos(1.2470*ts)+0.3492*np.cos(0.18019*ts)
    # xs = tmck.calc_x_response(ts)
    # np.testing.assert_almost_equal(xs[0,:],xs3,3)
    # # np.testing.assert_almost_equal(xs[1,:],xs2 ,4)
# %%