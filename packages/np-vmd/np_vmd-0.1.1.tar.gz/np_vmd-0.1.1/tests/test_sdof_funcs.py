
import pytest
from np_vmd.sdof_funcs import M, trans_ratio, log_decrement, r_Mpeak, M_peak,zeta_from_log_decrement 

def test_Mcalculation():
    
    pytest.approx(M(0.2, zeta=0.1),1.0408,abs=1e-4)
    assert M(0.2, zeta=0.1) ==pytest.approx(1.0408,abs=1e-4)
    pytest.approx(M(1.2, zeta=0.1),1.9952,abs=1e-4)
    pytest.approx(M(3.2, zeta=0.1),0.108,abs=1e-4)
    pytest.approx(M(0.2, zeta=1.5),0.8833,abs=1e-4)
    pytest.approx(M(1.2, zeta=1.5),0.2757,abs=1e-4)
    pytest.approx(M(3.2, zeta=1.5),0.0751,abs=1e-4)

def test_M_peak():
    
    pytest.approx(M_peak( zeta=0.1724),2.9435 ,abs=1e-4)
    pytest.approx(r_Mpeak( zeta=0.1724), 0.9698 ,abs=1e-4)
    

def test_Tcalculation():
    
    pytest.approx(trans_ratio(0.2, zeta=0.1),1.0416,abs=1e-4)
    pytest.approx(trans_ratio(1.2, zeta=0.1),2.0519,abs=1e-4)
    pytest.approx(trans_ratio(3.2, zeta=0.1),0.1282,abs=1e-4)
    pytest.approx(trans_ratio(0.2, zeta=1.5),1.0301,abs=1e-4)
    pytest.approx(trans_ratio(1.2, zeta=1.5),1.0302,abs=1e-4)
    pytest.approx(trans_ratio(3.2, zeta=1.5),0.7244,abs=1e-4)


def test_logarithmic_decrement_calc():
    
    pytest.approx(log_decrement( zeta=0.2),1.2825 ,abs=1e-4)
    pytest.approx(log_decrement( zeta=0.1724),1.1 ,abs=1e-4)
    pytest.approx(zeta_from_log_decrement( delta=1.2825),2 ,abs=1e-4)
    pytest.approx(zeta_from_log_decrement( delta=1.1),0.1724 ,abs=1e-4)
    