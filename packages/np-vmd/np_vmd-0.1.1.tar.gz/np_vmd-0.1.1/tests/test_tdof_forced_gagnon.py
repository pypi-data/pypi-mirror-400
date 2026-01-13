# TODO: this is not completed 

#%%
import pytest
import numpy as np
from np_vmd.tdof_MCK import TDOF_modal, MdofForcedResponseSingleExcitation



@pytest.fixture
def tmck()->TDOF_modal:
    '''pytest fixture for the forced response
    '''
    m1,m2  = 1000, 300
    k1,k2 = 4e5, 5e5
    c1, c2  = 2000, 2500
    F1_N=1000
    w_Exc_radps=30
    tmck = TDOF_modal(
        np.array([[m1,0],[0,m2]]), 
        K=np.array([[k1,-k1],[-k1,k1+k2]]), 
        C= np.array([[c1,-c1],[-c1,c1+c2]]))
    return tmck


@pytest.fixture
def r_forced(tmck)->MdofForcedResponseSingleExcitation:
    '''pytest fixture for the forced response
    '''
    r_forced = MdofForcedResponseSingleExcitation(mdof_sys=tmck, node=0, Fmag=1000, w_exc_radps=30, phi_exc_rad=0)
    r_forced.set_iv(x0s = np.array([[0, 0]]).T,dx0s=np.array([[0,0]]).T)
    return r_forced

def test_tmck_fixture(tmck, r_forced):
    """
    this is from Iannic Gagnon's Youtube video
    https://www.youtube.com/watch?v=sqdd0ja1PXM&t=1s

    TODO: complete this test
    """
    # Test the matrices returned by tmck.mM, tmck.mC, and tmck.mK
    np.testing.assert_equal(tmck.mM, np.array([[1000, 0], [0, 300]]))
    np.testing.assert_equal(tmck.mC, np.array([[2000, -2000], [-2000, 4500]]))
    np.testing.assert_equal(tmck.mK, np.array([[400000, -400000], [-400000, 900000]]))

    np.testing.assert_allclose(tmck.Ktilde, 
            np.array([[ 400.        , -730.29674334],
                       [-730.29674334, 3000.        ]]),rtol=1e-5)

    np.testing.assert_allclose(tmck.Ctilde, 
            np.array(
                [[ 2.        , -3.65148372],
                 [-3.65148372, 15.        ]]),rtol=1e-5)

    np.testing.assert_allclose(tmck.ls, 
            np.array([ 208.91538358, 3191.08461642]),rtol=1e-5)

    # modeshapes 
    np.testing.assert_allclose(tmck.vs, 
            np.array(
                [[-0.9674318 ,  0.25313181],
                 [-0.25313181, -0.9674318 ]]),rtol=1e-5)

    np.testing.assert_allclose(tmck.Smat, 
            np.array([
                [-0.03059288,  0.00800473],
                [-0.01461457, -0.0558547 ]]),rtol=1e-5)


    np.testing.assert_allclose(tmck.zs, 
            np.array([0.03613476, 0.14122421]),rtol=1e-5)
    # TODO crosscheck this with the original source (YOUtube)
    np.testing.assert_allclose(tmck.Smat.T.dot(tmck.mC.dot(tmck.Smat))
            , np.array([[1.04457692e+00, 0.00000000e+00],
                [5.55111512e-16, 1.59554231e+01]]),atol=1e-5)

def test_tmck_modal_total_response(tmck):
    F1_N=1000
    w_Exc_radps=30
    phi_Exc_rad=0
    node=0
    r_mdof = MdofForcedResponseSingleExcitation(
        mdof_sys = tmck, 
        node=node, 
        Fmag=F1_N, 
        w_exc_radps=w_Exc_radps, 
        phi_exc_rad=phi_Exc_rad)
    
    np.testing.assert_allclose(r_mdof.Fmag_pc, [-30.5928797, 8.00473059],rtol=1e-5)
    
    r_mdof.calc_response()
    assert r_mdof.lst_modal_response_params[0].get('Xss') == pytest.approx(-0.044222480393594145 ,rel=1e-4)
    assert r_mdof.lst_modal_response_params[0].get('phi_ss') == pytest.approx(0.17339271361497388,rel=1e-4)
    assert r_mdof.lst_modal_response_params[0].get('X_tra') == pytest.approx(0.04691381091720522,rel=1e-4)
    assert r_mdof.lst_modal_response_params[0].get('phi_tra') == pytest.approx(0.3804495998755305,rel=1e-4)
    # second 
    assert r_mdof.lst_modal_response_params[1].get('Xss') == pytest.approx(0.003420017320299711 ,rel=1e-4)
    assert r_mdof.lst_modal_response_params[1].get('phi_ss') == pytest.approx(0.15028189271655545, rel=1e-4)
    assert r_mdof.lst_modal_response_params[1].get('X_tra') == pytest.approx(0.0034651808087259525, rel=1e-4)
    assert r_mdof.lst_modal_response_params[1].get('phi_tra') == pytest.approx(-2.9213400807651495, rel=1e-4)
    
    np.testing.assert_allclose(r_mdof.angle_2dArray,
            np.array([
                [0.98500511, 0.17252518],
                [0.98872891, 0.14971685]]),rtol=1e-5)
    np.testing.assert_allclose(r_mdof.xs_ABmag_orig,
            np.array([
                [1.35967429e-03, 2.37506803e-04],
                [4.47730527e-04, 8.29022273e-05]]),rtol=1e-5)
# %%
