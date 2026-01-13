import pytest
import numpy as np
from np_vmd.tdof_MCK import TDOF_modal


def test_modal_inman_4_1_1():
    # examples 4.1.1. to 4.2.6
    m1,m2  = 9,1
    k1=24
    k2=3
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]))
    np.testing.assert_equal(tmck.Ktilde, np.array([[3,-1],[-1,3]]))
    #eigenvalues
    np.testing.assert_almost_equal(tmck.ls, np.array([4,2]),4)
    #eigenfrequencies
    np.testing.assert_almost_equal(tmck.wns, np.array([2, 1.41421]),4) 
    #eigenvectors
    np.testing.assert_almost_equal(tmck.vs, np.array([[0.70710678 ,0.70710678 ],[-0.70710678 , 0.70710678 ]]),4)
    #eigenmodes
    np.testing.assert_almost_equal(tmck.us, np.array([[1,1],[-0.333333, 0.3333333]]),4)
    np.testing.assert_almost_equal(tmck.Lambda_mat, np.array([[4, 0], [0, 2]]),4)
    np.testing.assert_almost_equal(tmck.Lambda_mat, np.diag([4,  2]),4)


def test_Inman_4_2_6():
    # example Inman  4.2.6
    m1 , m2 = 1,4
    k1, k2, k3=10,2, 10
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2+k3]]))
    np.testing.assert_equal(tmck.Ktilde, np.array([[12,-1],[-1,3]]))
    #eigenvalues
    np.testing.assert_almost_equal(tmck.ls, np.array([12.10977,2.89022]),4)
    #eigenfrequencies
    np.testing.assert_almost_equal(tmck.wns, np.array([3.4799098, 1.70006699]),4) 
    #eigenvectors
    np.testing.assert_almost_equal(tmck.vs, np.array([[0.99402894,0.10911677],[-0.10911677, 0.99402894]]),4)
    #eigenmodes
    np.testing.assert_almost_equal(tmck.us, np.array([[1,1],[-0.21954446, 18.21954446]]),4)

    np.testing.assert_almost_equal(tmck.Lambda_mat, np.array([[1.21097722e+01, 2.22044605e-16], [5.55111512e-17, 2.89022777e+00]]),4)

# %%
    
def test_modal_raisingValueError():
    '''
    this is a test for testing impoper mass matrices. 
    '''
    # examples 4.1.1. to 4.2.6
    m1,m2  = 9,1
    k1=24
    k2=3
    with pytest.raises(ValueError):
        tmck = TDOF_modal(np.array([[m1,0],[0,m2],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]))



def test_calc_C_from_Z():
    """
    Test function for the `calc_C_from_Z` method of the `TDOF_modal` class.
    """
    m1,m2  = 9,1
    k1=24
    k2=3
    c1 = 2.4
    c2 = 0.3
    C = np.array([[c1+c2,-c2],[-c2,c2]])
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]), C= C)
    
    np.testing.assert_almost_equal(C,tmck.calc_C_from_Z(tmck.zs).mC, 3)
    np.testing.assert_almost_equal(C,tmck.calc_C_from_Z(np.diag(tmck.zs)).mC, 3)

def test_tdof_damping_inman_4_5_1():
    ''' With damping and forced

    # numerical value from Inman 4th ed. Engineering Vibration, example: 4.5.1. 
    '''
    m1,m2  = 9,1
    k1=24
    k2=3
    c1 = 2.4
    c2 = 0.3 
    F0=3
    w0=2
    tmck = TDOF_modal(np.array([[m1,0],[0,m2]]), K=np.array([[k1+k2,-k2],[-k2,k2]]), C= np.array([[c1+c2,-c2],[-c2,c2]]))
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

    tmck.update_damping(  np.array([0.1, 0.05]))
    np.testing.assert_almost_equal(tmck.zs, np.array([0.1,0.05]), 4)
    np.testing.assert_almost_equal(tmck.wds, np.array([1.9900,1.4124]), 3)

    #eigenvectors
    np.testing.assert_almost_equal(tmck.vs, np.array([[0.70710678 ,0.70710678 ],[-0.70710678 , 0.70710678 ]]),4)
    #eigenmodes
    np.testing.assert_almost_equal(tmck.us, np.array([[1,1],[-0.333333, 0.3333333]]),4)
    np.testing.assert_almost_equal(tmck.Lambda_mat, np.array([[4, 0], [0, 2]]),4)
    np.testing.assert_almost_equal(tmck.Lambda_mat, np.diag([4,  2]),4)
    


