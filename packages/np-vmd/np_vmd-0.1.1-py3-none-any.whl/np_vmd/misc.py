#%%
from numpy import pi
import numpy as np
class AngularFrequency():
    """Angular Frequency object
    """    
    def __init__(self, w):
        self.w = w
    
    @classmethod
    def from_rpm(cls, rpm:float):
        """Create an AngularFrequency object from rpm (Factory class method)

        Args:
            rpm (float): revolutions per minute

        Returns:
            AngularFrequency: _description_
        """        
        return cls(2*pi/60 *rpm)


    @classmethod
    def from_r_wn(cls, r:float, wn:float):
        """Factory class method 

        Args:
            r ([float]): ratio of frequencies
            wn ([float]): eigenfrequency

        Returns:
            [float]: frequency
        """        
        return cls(r*wn)

#%%
def convert_harmonic_to_cos(A, B):
    """
    Converts harmonic motion in the form
        A*cos(w*t)+ B*sin(w*t) 
    to 
        X*cos(w*t + phi).

    based on the identity:  
        cos(wt+phi) = cos(wt)*cos(phi) - sin(wt)*sin(phi)
    Because
        X* cos(wt+phi) = X*cos(wt)*cos(phi) - X*sin(wt)*sin(phi)
    We can compare the coefficients to get:
        A = X*cos(phi)
        B = -X*sin(phi)
    Solving for X and phi:
        X = sqrt(A**2 + B**2)
        phi = arctan2(-B, A)
        
    Parameters:
    A (float): The cos coefficient.
    B (float): The sin coefficient.

    Returns:
    X (float): The magnitude of the harmonic motion.
    phi (float): The angle of the harmonic motion.
    """
    X = np.sqrt(A**2 + B**2)
    phi = np.arctan2(-B, A)
    return X, phi

def convert_harmonic_to_sin(A, B):
    """
    Converts harmonic motion in the form
        A*cos(w*t)+ B*sin(w*t) 
    to 
        X*sin(w*t + phi).

    based on the identity:
        sin(wt+phi) = cos(wt)*sin(phi) + sin(wt)*cos(phi)
    Because
        X* sin(wt+phi) = X*cos(wt)*sin(phi) + X*sin(wt)*cos(phi)
    We can compare the coefficients to get:
        A = X*sin(phi)
        B = X*cos(phi)
    Solving for X and phi:
        X = sqrt(A**2 + B**2)
        phi = arctan2(A, B)
        
    Parameters:
    A (float): The cos coefficient.
    B (float): The sin coefficient.

    Returns:
    X (float): The magnitude of the harmonic motion.
    phi (float): The angle of the harmonic motion.
    """
    X = np.sqrt(A**2 + B**2)
    phi = np.arctan2(A, B)
    return X, phi
# TODO: add conversion to exponential form
# TODO: add conversion to complex form
class HarmonicMotion():
    """Harmonic motion object

    The HarmonicMotion class represents a harmonic motion 
    with cosine and sine coefficients.
    
    It provides methods to convert the harmonic motion 
    to different forms and create instances from different representations. 
    
    The class also includes factory class methods for creating
    HarmonicMotion objects from magnitude and phase angle.
    """

    A = None # cos coefficient
    B = None # sin coefficient
    def __init__(self, A,B) :
        self.A = A
        self.B = B  
    
    def to_X_cos_phi(self):
        """Converts harmonic motion in the form
        A*cos(w*t)+ B*sin(w*t) 
        to 
        X*cos(w*t + phi).
        """
        
        return convert_harmonic_to_cos(self.A, self.B)

    def to_X_sin_phi(self):
        """Converts harmonic motion in the form of 
            X*sin(w*t + phi).
        """
        return convert_harmonic_to_sin(self.A, self.B)

    @classmethod
    def from_X_cos_phi(cls, X, phi):
        """Factory class method
         a HarmonicMotion object from X*cos(w*t+phi)

        Args:
            X ([float]): magnitude
            phi ([float]): phase angle
        """
        A = X*np.cos(phi)
        B = -X*np.sin(phi)
        return cls(A,B)

    @classmethod
    def from_X_sin_phi(cls, X, phi):
        """Factory class method that creates 
        a HarmonicMotion object from X*sin(w*t+phi)

        Args:
            X ([float]): magnitude
            phi ([float]): phase angle
        """
        A = X*np.sin(phi)
        B = X*np.cos(phi)
        return cls(A,B)

# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt 

    w = 1 
    t = np.linspace(0, 10, 1000)
    A=1
    B=2
    h1 = A*np.cos(w*t)+B*np.sin(w*t)
    xcos,pc = convert_harmonic_to_cos(A, B)
    xsin,psin = convert_harmonic_to_sin(A, B)
    plt.plot(t, h1, label="h1")	
    plt.plot(t, xcos*np.cos(w*t+pc), label="cos")	
    plt.plot(t, xsin*np.sin(w*t+psin), label="sin")	
    plt.legend()

# %%
if __name__ == "__main__":
    A = 1
    B = 2
    motion = HarmonicMotion(A=1, B=2)
    Xc, pcos = motion.to_X_cos_phi()
    Xs, psin = motion.to_X_sin_phi()
    assert Xc == Xs
    hm_cos = HarmonicMotion.from_X_cos_phi(Xc, pcos)
    hm_sin = HarmonicMotion.from_X_sin_phi(Xs, psin)
    assert hm_cos.A == hm_sin.A
    assert hm_cos.B == hm_sin.B
    assert hm_cos.A == A
    assert hm_cos.B == B
# %%
