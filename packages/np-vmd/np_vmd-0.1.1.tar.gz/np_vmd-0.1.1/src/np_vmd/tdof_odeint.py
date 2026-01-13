#%% [markdown]
# this is the verion of TDOF that uses numerical integration to obtain the response
#
# There is also the TDOF_MCK that uses **modal analysis** to obtain the response, 
# which is more analytical and faster.
#%%
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
class Tdof_params():
    def __init__(self, m1=1, m2=1, c1=0, c2=0, k1=1, k2=1):
        self.m1=m1
        self.m2=m2
        self.c1=c1
        self.c2=c2
        self.k1=k1
        self.k2=k2

class Mdof_params():
    def __init__(self, ms:np.array=None, cs:np.array=None, ks:np.array=None):
        self.ms=ms
        self.cs=cs
        self.ks=ks

class Tdof_system():
    def __init__(self, tdof_params:Tdof_params, A=None):
        self.params = tdof_params
        self.A=A
        self.sys_fn = self.gen_system_model_2dof_mat()

    # define system model
    def gen_system_model_2dof_mat(self):
        """Generates a function for the odeint based on state space matricess
        Model with the use of a matrix y = A*x + F
        """
        # Inputs (2):

        def system_model_2dof_mat(x,t,Fs):
            """
            """
            B=np.array([0 ,0,Fs[0]/self.params.m1,Fs[1]/self.params.m2])
            # States (2):
            # print(Fs[0], Fs[1])
            xdot = self.A.dot(x) + B
            # Return derivatives
            return xdot
        return system_model_2dof_mat

    def set_time(self, tmax=1, no_points=101 ):
        self.no_points = no_points
        self.ts = np.linspace(0,tmax,no_points)

    def set_F1(self, F1):
        self.F1 = np.vectorize(F1)
    def set_F2(self, F2):
        self.F2 = np.vectorize(F2)
    def set_y0(self, x1_0=0.0, x2_0=0.0, v1_0=0.0, v2_0=0.0):
        self.y0 = [x1_0, x2_0, v1_0, v2_0]

    def perform_simulation(self):
        F1 = self.F1(self.ts)
        F2 = self.F2(self.ts)
        self.Fs = np.stack([F1,F2])
        self.xms = self._perform_simulation(t=self.ts, y0=self.y0, Fs=self.Fs)
        return self.xms

    def _perform_simulation(self, t, y0, Fs):
        """wrapper function fo the analysis 

        Args:
            t (time): ndarray (len(t),)
            y0 (initial conditions): ndarray (4,)
            Fs (Forces): ndarray (2, len(t))

        Returns:
            _type_: _description_
        """        
        # Storage for results
        xms = np.zeros((len(t), 4))
        xms [0,:] = y0
        # Loop through each time step
        for i in range(len(t)-1):
            # Simulate
            inputs = (Fs[:,i],)
            ts = [t[i],t[i+1]]
            y = odeint(self.sys_fn, y0, ts, args=inputs)
            xms[i+1,:] = y[-1]
            # Adjust initial condition for next loop
            y0 = y[-1]
        return xms 

    def plot_response(self):
        # Plot the inputs and results
        plt.figure()
        plt.subplot(3,1,1)
        plt.plot(self.ts,self.Fs[0,:],'k-',label='F1')
        plt.plot(self.ts,self.Fs[1,:],'r--',label='F2')
        plt.legend(loc='best')

        plt.subplot(3,1,2)
        plt.plot(self.ts,self.xms[:,0],'-',label='x1m')
        plt.plot(self.ts,self.xms[:,1],'-',label='x2m')
        plt.xlabel('time')
        plt.ylabel('Displacement [m]')
        plt.legend(loc='best')

        plt.subplot(3,1,3)
        plt.plot(self.ts,self.xms[:,2],'-',label='v1m')
        plt.plot(self.ts,self.xms[:,3],'-',label='v2m')
        plt.xlabel('time')
        plt.ylabel('Velocity [m/s]')
        plt.legend(loc='best')

        plt.figure()
        plt.plot(self.ts,2+self.xms[:,0],'-',label='x1m')
        plt.plot(self.ts,self.xms[:,1],'-',label='x2m')
        plt.xlabel('Time [s]')
        plt.ylabel('x [m]')
#%%

if __name__=="__main__":

    tps = Tdof_params(m1=9,m2=1,c1=0,c2=0, k1=24,k2=3)
    A= np.array([
        [ 0 ,0 , 1, 0],
        [ 0 ,0 , 0, 1],
        [-(tps.k1+tps.k2)/tps.m1, +tps.k1/tps.m1 , -2*tps.c1/tps.m1, +tps.c2/tps.m1],
        [ tps.k2/tps.m2 , -tps.k2/tps.m2, tps.c1/tps.m2 , -3*tps.c2/tps.m2 ]
    ])

    ts = Tdof_system(tps,A)

    # set time
    niter = 1001
    t = np.linspace(0,40,niter)

    # Initial Conditions
    # y0 = [x1_0, x2_0,v1_0,v2_0]
    # y0 = [1/3, -1, 0, 0]
    # F1 = np.ones(len(t))*0.0
    # F2 = np.ones(len(t))*0.0
    # Fs = np.stack([F1,F2])
    ts.set_time(tmax=40,no_points=niter)
    ts.set_F1(lambda x: 13*np.cos(2*np.pi*3*x) )
    ts.set_F2(lambda x: 0 )
    ts.set_y0(x1_0=1, x2_0=1/3, v1_0=0, v2_0=0)
    xms = ts.perform_simulation()
    print(xms)
    ts.plot_response()
#%%
    import matplotlib.pyplot as plt
    plt.plot(t, xms[:,0])
    plt.plot(t, xms[:,1])
    plt.show()
# %%

# %%
