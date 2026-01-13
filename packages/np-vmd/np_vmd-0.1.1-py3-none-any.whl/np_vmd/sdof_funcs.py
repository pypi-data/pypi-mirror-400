#%%
import numpy as np

class SDOF_system():
    #TODO the SDOF system class requires severe rework 
    # because it assumes that the system is always underdamped.
    def __init__(self, m:float, k:float, c:float= 0):
        self.m = m
        self.k = k
        self.c = c
        self.__params__()

    def __params__(self):
        self.wn = np.sqrt(self.k/self.m)
        self.zeta = self.c/(2*self.m*self.wn)
        self.T = (2*np.pi)/self.wn # period no damping

        # From https://en.wikipedia.org/wiki/Q_factor
        self._Q_factor = 1/(2*self.zeta) # Quality factor
        self._alpha = self.zeta*self.wn # attenuation factor
        self._tau = 1/self._alpha  
        
        if self.zeta<1:
            self.wd = self.wn *np.sqrt(1-self.zeta**2)
            self.delta = log_decrement(self.zeta) # logaritmic decretemnt            
            self.Td = (2*np.pi)/self.wd # damping period
        else:
            self.wd = None #damping frequency
            self.delta = None
            self.Td = None

    @property
    def alpha(self):
        """ attenuation factor alpha
        
        The envelope of oscillation decays proportional 
        to $e^{-alpha t}$ or $e^{−t/τ}$, where  
        and τ can be expressed as:
        
        $$alpha = \zeta\cdot w_n$$

        https://en.wikipedia.org/wiki/Q_factor

        Returns:
            _type_: _description_
        """        
        return self._alpha
    
    @property
    def tau(self):
        """ exponential time constant
        
        The envelope of oscillation decays proportional 
        to $e^{-alpha t}$ or $e^{−t/τ}$, where  
        and τ can be expressed as:
        
        $$tau = 1/(\zeta\cdot w_n)$$

        https://en.wikipedia.org/wiki/Q_factor

        Returns:
            _type_: _description_
        """        
        return self.tau

    def c_crit(self):
        """returns the critical value

        Returns:
            _type_: _description_
        """        
        return 2 * self.m*self.wn

    def amplitude(self, x0, v0):
        ''' amplitude for free under-damped vibrations

        representing the solution $X0*np.exo(-zeta*wn*t)*np.sin(wd*t + phi)$

        From RAO  eq. 2.73, eq.2.74
        return np.sqrt((x0*self.wn)**2 + (v0)**2 + 2*x0*v0*self.zeta*self.wn)/self.wd
        '''
        
        return np.sqrt(x0**2 + ( (v0 + x0*self.zeta*self.wn )/self.wd)**2)

    def phase_cos(self, x0, v0):
        ''' Phase $phi$ for free under-damped vibrations

        representing the solution $X0*np.exo(-zeta*wn*t)*np.cos(wd*t - phi)$

        From RAO  eq. 2.73, eq.2.74
        '''
        
        # wn = self.wn
        # wd = self.wd
        return np.arctan2(v0+self.zeta*self.wn*x0, x0 *self.wd) 

    def phase_sin(self, x0, v0):
        ''' Phase $phi$ for free under-damped vibrations for sin

        representing the solution $X0*np.exp(-zeta*wn*t)*np.sin(wd*t + phi)$

        From RAO  eq. 2.73, eq.2.74
        '''
        
        # wn = self.wn
        # wd = self.wd
        return np.arctan2(x0 *self.wd, v0+self.zeta*self.wn*x0) 

    def free_response_at_t(self, t:np.array, x0:float, v0:float)->dict:
        """returns the free response at a specific time.

        Args:
            t (float): time in s
            x0 (float): position at t=0
            v0 (float): velocity at t=0

        Returns:
            dict: [description]
        """        
        #TODO: complete this
        A = self.amplitude(x0,v0)
        phi = self.phase_cos(x0,v0)

        if self.zeta<1:
            # Ae^{-zeta \omega_n t}\cos(\omega_d t + \phi)\) 
            xs = A*np.exp(-self.zeta*self.wn*t)*np.cos(self.wd*t - phi)
            vs = -(np.cos(self.wd*t -phi)*self.wn*self.zeta + self.wd*np.sin(self.wd*t - phi) ) *A*np.exp(-self.zeta*self.wn*t)
        else:
            raise Exception('Not implemented yet')
        return {'t':t, 'xs':xs,'vs':vs}

    def free_response_at_t_funcs(self, x0:float, v0:float)->dict:
        """returns the free response function using a cos function

        Args:
            t (float): time in s
            x0 (float): position at t=0
            v0 (float): velocity at t=0

        Returns:
            dict: [description]
        """
        if self.zeta<0:
            raise (ValueError('zeta should be greater than 0'))

        if self.zeta<1:
            A = self.amplitude(x0,v0)
            phi = self.phase_cos(x0,v0)
            # Ae^{-zeta \omega_n t}\cos(\omega_d t + \phi)\) #TODO check equations for sign
            xf = lambda t: A*np.exp(-self.zeta*self.wn*t)*np.cos(self.wd*t - phi)
            vf = lambda t: -(np.cos(self.wd*t - phi)*self.wn*self.zeta + self.wd*np.sin(self.wd*t -phi) ) *A*np.exp(-self.zeta*self.wn*t)
        elif self.zeta==1:
            xf = lambda t:          np.exp(-self.wn*t) * (x0 + (v0+ self.wn*x0)*t )
            # vf = lambda t: -self.wn*np.exp(-self.wn*t) * (x0 + (v0+ self.wn*x0)*t ) + np.exp(-self.wn*t) * (v0+ self.wn*x0 )
            # vf = lambda t: np.exp(-self.wn*t) *( (v0 + self.wn*x0 ) - self.wn*(x0 + (v0+ self.wn*x0)*t ) )
            vf = lambda t: np.exp(-self.wn*t) *( (v0*(1- self.wn*t) - self.wn**2 *x0*t ) )
        elif self.zeta>1:
            z2m1 = np.sqrt(self.zeta**2-1)
            C1=  (v0/self.wn + x0*(self.zeta + z2m1))
            C2= -(v0/self.wn + x0*(self.zeta - z2m1))
            xf = lambda t: np.exp(-self.zeta*self.wn*t)/(2*z2m1)*(C1*np.exp(z2m1*self.wn*t) +C2*np.exp(-z2m1*self.wn*t))
            vf = lambda t: np.exp(-self.zeta*self.wn*t)/(2*z2m1)*(
                z2m1*self.wn*(C1*np.exp(z2m1*self.wn*t) - C2*np.exp(-z2m1*self.wn*t)) -
                self.zeta*self.wn*(C1*np.exp(z2m1*self.wn*t) + C2*np.exp(-z2m1*self.wn*t)) 
                  )
        
        return {'x':xf,'v':vf}
    
    def forced_cos_response_at_t_funcs(self, x0:float, v0:float, F0:float , w:float)->dict:
        """returns the forced response function 
        (currently only the partail part 
        todo add total and homoegeneous)

        Args:
            t (float): time in s
            x0 (float): position at t=0
            v0 (float): velocity at t=0
            F0 (float): Force magnitude [N] 
            w (float): excitation frequency [rad/s]
            #TODO add theta_exc

        Returns:
            dict: [description]
        """ 
        # partial solutions rao p.213 eq3.28, 3.29
        #
        X_p= F0/np.sqrt( (self.k-self.m*w**2)**2 + (self.c*w)**2)
        phi_p = np.arctan2(self.c*w, self.k - self.m*w)
        x_partial = lambda t: X_p * np.cos(w*t-phi_p)

        X0 = np.sqrt( (x0- X_p*np.cos(phi_p))**2 
                + 1/(self.wd**2)*(self.zeta*self.wn*(x0-X_p*np.cos(phi_p))+v0-w*X_p*np.sin(phi_p))**2)    
        phi_0 = np.arctan2(self.zeta*self.wn*(x0-X_p*np.cos(phi_p))+v0-w*X_p*np.sin(phi_p), self.wd*(x0- X_p*np.cos(phi_p)) )
        if self.zeta<1:
            # RAO equation 3.35 
            xf = lambda t: X0*np.exp(-self.zeta*self.wn*t)*np.cos(self.wd*t - phi_0) + X_p * np.cos(w*t-phi_p)
            vf = lambda t: -X0**np.exp(-self.zeta*self.wn*t)*(self.zeta*self.wn*np.cos(self.wd*t - phi_0)  + self.wd*np.sin(self.wd*t-phi_0)
                ) - X_p *w * np.sin(w*t - phi_p)
        else:
            raise (Exception('Not implemented yet'))
        
        return {'x':xf,'v':vf, "x_partial":x_partial}

    def response_params(self, x0: float, v0: float, F0: float, w: float):
        """
        Returns the parameters of the total solution for excitation F0*cos(wt).

        Args:
            x0 (float): Initial displacement.
            v0 (float): Initial velocity.
            F0 (float): Force amplitude.
            w (float): Excitation frequency.

        Returns:
            dict: A dictionary containing the following parameters:
                - "Xss" (float): Steady-state amplitude of the response.
                - "phi_ss" (float): Steady-state phase angle of the response.
                - "X_tra" (float): Transient amplitude of the response.
                - "phi_tra" (float): Transient phase angle of the response.
                - "form" (str): String representation of the response equation.

        """
        X_p = F0 / np.sqrt((self.k - self.m * w ** 2) ** 2 + (self.c * w) ** 2)
        phi_p = np.arctan2(self.c * w, self.k - self.m * w)
        X_0 = np.sqrt((x0 - X_p * np.cos(phi_p)) ** 2 + 1 / (self.wd ** 2) * (
                self.zeta * self.wn * (x0 - X_p * np.cos(phi_p)) + v0 - w * X_p * np.sin(phi_p)) ** 2)
        phi_0 = np.arctan2(self.zeta * self.wn * (x0 - X_p * np.cos(phi_p)) + v0 - w * X_p * np.sin(phi_p),
                           self.wd * (x0 - X_p * np.cos(phi_p)))
        return {"Xss": X_p, "phi_ss": phi_p, "X_tra": X_0, "phi_tra": phi_0,
                "form": f"{X_0:.5g}*cos({self.wn:.5g}*t{-phi_0:+.5g}) {X_p:+.5g}*cos({w:.5g}*t{-phi_p:+.5g})",
                "x_lambda": lambda t: X_0 * np.cos(self.wn * t - phi_0) + X_p * np.cos(w * t - phi_p)}

    @classmethod
    def from_zeta(cls, zeta:float, m, k):
        return cls(m=m, k=k, c=2*zeta*np.sqrt(m*k))

    @classmethod
    def from_z_mk(cls, zeta:float, m, k):
        return cls(m=m, k=k, c=2*zeta*np.sqrt(m*k))

    @classmethod
    def from_wn_kc(cls, wn:float, k:float, c:float):
        return cls(m=k/wn**2, k=k, c=c)

    @classmethod
    def from_wn_mc(cls, wn:float, m:float, c:float):
        return cls(m=m, k=m*wn**2, c=c)

    @classmethod
    def from_wn_mz(cls, wn:float, m:float, zeta:float):
        return cls(m=m, k=m*wn**2, c=2*zeta*m*wn)

    @classmethod
    def from_wn_kz(cls, wn:float, k:float, zeta:float):
        return cls(m=k/wn**2, k=k, c=2*zeta*wn/k)

def log_decrement(zeta:float):
    """Calculation of log decrement from Zeta

    Args:
        zeta (_type_): damping ratio needs to be between 0 and 1

    Returns:
        floadt: log decrement i.e. $\delta = log(X_{i+1}/X_{i})$
    """    
    if zeta<0 or  zeta>1:
        raise ValueError('zeta should be between 0 and 1')
    return (2*np.pi*zeta)/np.sqrt(1-zeta**2)


def zeta_from_log_decrement(delta):
    ''' Calculation of zeta based on logarithmic decrement

    require delta in log(X_{i+1}/X_{i})
    '''
    return delta/np.sqrt(4*np.pi**2 +delta**2)

def M(r, zeta):
    ''' Magnification factor
    '''
    return np.sqrt( 1/((1-r**2)**2+ (2*r*zeta)**2) )

def M_peak(zeta):
    ''' Peak Magnification factor
    '''
    return 1/(2*zeta*np.sqrt( 1-zeta**2 ))

def r_Mpeak(zeta):
    ''' r where maximum Magnification factor occurs
    '''
    return np.sqrt( 1-2*zeta**2 )

def phi_angle(r:float, zeta:float):
    """phase angle calculation

    Args:
        r (float): frequency ratio
        zeta (:float): damping ratio

    Returns:
        float: phase angle in rad
    """    
    ''' 
    '''
    return np.arctan2(2*zeta*r, 1- r**2)


def trans_ratio(r, zeta):
    ''' Transmissability ratio
    '''
    return np.sqrt( (1+ (2*r*zeta)**2)/((1-r**2)**2+ (2*r*zeta)**2) )

if __name__ == "__main__":
    rs= np.linspace(0,1,10)
    print(trans_ratio(rs, 0.1))
# %%
