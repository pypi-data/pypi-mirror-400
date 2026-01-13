#%% [markdown]

# Class for the solution of a simple harmonic oscillator of 1 sdof
# with plotting abilities. 
#%% 
import numpy as np
from numpy import random 
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy import signal
from matplotlib import animation

import numpy as np
import matplotlib.pyplot as plt

class SHO_sdof_sys():
    def __init__(self, m=1, c=0, k=1):
        self._m = m
        self._c = c
        self._k = k


class SHO_results():
    ''' contains and plots results'''
    def __init__(self, sho_sys, t, Fs, xs, vs, y0=[0,0] ,desc=""):
        self.sho_sys = sho_sys
        self.desc = desc
        self.y0 = y0
        self.t = t
        self.F = Fs
        self.xs = xs
        self.vs = vs

        self.niter = len(self.t)

    def plot_results(self):
        # Plot the inputs and results
        fig, ax = plt.subplots(3,1,sharex=True)
        plt.suptitle('m={}, c={}, k= {}: {}'.format(
            self.sho_sys._m, self.sho_sys._c,self.sho_sys._k, self.desc))
        
        ax[0].plot(self.t,self.F,'k-',label='F')
        ax[0].legend(loc='best')
        ax[0].set_ylabel('Force')

        ax[1].plot(self.t,self.xs,'.',label='x')
        ax[1].legend(loc='best')
        ax[1].set_ylabel('Displacement')

        ax[2].plot(self.t,self.vs,'.',label='v')
        ax[2].legend(loc='best')
        ax[2].set_ylabel('Velocity')


    def create_animated_plot(self, xlim =(-3, 3), ylim = [-3, 8]):
        # create animated plot
        def create_box_outline(box_h = 1,box_w = 2):
            # box data
            box_x = np.array([-1,-1,1,1,-1])*box_w/2
            box_y = np.array([-1,1,1,-1,-1])*box_h/2
            return np.vstack((box_x,box_y))


        box_xy = create_box_outline(box_h = 1,box_w = 2)
        box1 =  np.array([np.zeros(self.niter), self.xs])
        box_list = [box1]

        # init figures
        # fig = plt.figure()
        # ax1 = plt.axes(  xlim=xlim, ylim=ylim)
        fig, (ax1,ax2) = plt.subplots(2,1)
        ax1.set_xlim(xlim)
        ax1.set_ylim(ylim)
        line, = ax1.plot([], [], lw=2)
        ax1.set_ylabel('position')

        ax2.plot(self.t, self.xs)
        ax2.set_xlabel('time')
        ax2.set_ylabel('position')

        plotcols = ["black","red"]
        lines = []
        for index in range(1):
            lobj = ax1.plot([],[],lw=2,color=plotcols[index])[0]
            lines.append(lobj)
        lines.append(ax2.axvline(x=0, c='red'))

        def init():
            lines[0].set_data([],[])
            return lines

        def animate(i):
            x1 = box_list[0][0, i]
            y1 = box_list[0][1, i]

            xs = [x1]
            ys = [y1]

            lines[0].set_data(box_xy[0,:]+xs[0], box_xy[1,:]+ys[0]) 
            lines[1].set_xdata(self.t[i]) 
            return lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        self.anim = animation.FuncAnimation(fig, animate, init_func=init,
                                    frames=self.niter, interval=10, blit=True)


class SHOSdofSolver():
    """
    A class used to represent and solve a Single Degree of Freedom (SDOF) 
    Simple Harmonic Oscillator (SHO) system.

    ...

    Attributes
    ----------
    _m : float
        mass of the system
    _c : float
        damping coefficient of the system
    _k : float
        stiffness of the system
    _sys_fn : function
        function representing the system model

    Methods
    -------
    gen_system_model_1dof_mat():
        Generates a function for the odeint based on state space matrices.

    perform_simulation(t, y0, Fs, desc=""):
        Performs a simulation of the system over time.
    """  
    def __init__(self, m=1, c=0, k=1):
        self._m = m
        self._c = c
        self._k = k

        self._sys_fn = self.gen_system_model_1dof_mat()

    # define system model
    def gen_system_model_1dof_mat(self):
        """Generates a function for the odeint based on state space matricess
        Model with the use of a matrix y = A*x + F
        """
        # Inputs (2):
        A= np.array([
            [ 0 ,1 ],
            [-self._k/self._m, -self._c/self._m]
        ])

        def system_model_1dof_mat(x,t,F2):
            """
            """
            B=np.array([0 ,F2/self._m])
            # States (2):
            xdot = A.dot(x) + B
            # Return derivatives
            return xdot
        return system_model_1dof_mat

    def perform_simulation(self, t, y0, Fs, desc=""):
        # Storage for results
        xms = np.zeros((len(t), 2))
        xms[0,:] = y0
        # Loop through each time step
        for i in range(len(t)-1):
            # Simulate
            inputs = (Fs[i],)
            ts = [t[i],t[i+1]]
            y = odeint(self._sys_fn,y0,ts,args=inputs)
            xms[i+1,:] = y[-1]
            # Adjust initial condition for next loop
            y0 = y[-1]
        sho_res = SHO_results(self, t, Fs, xs=xms[:,0], vs=xms[:,1], y0=y0, desc=desc)
        return sho_res

#%% simple animation of a mass.

#%%
if __name__ == "__main__":
    plt.rcParams["font.size"] = "15"

    # system definition
    m1= 1
    c1 = 0.5
    k = 3
    sho = SHOSdofSolver(m=m1, c=c1, k=k)

#%% 
    # set analysis time
    niter = 1001
    t = np.linspace(0,40,niter)

    # Initial Conditions
    x1_0 = 2
    v1_0 = -1
    y0 =[x1_0, v1_0]

    # Force excitation
    F2 = np.ones(len(t))*0.0
    F2[:] = 0
    F2 = 3*np.sin(1*t) + 2*np.sin(3*t) 
    # F2[0:100] = 6
    # F2[100:125] = 9
    # F2[126:]=0
    sho1res = sho.perform_simulation(t, y0=y0, Fs=F2)
    sho1res.plot_results()

# #%% 
    # Initial Conditions
    x1_0 = 0
    v1_0 = 0
    y0 =[x1_0, v1_0]

    # Force excitation
    F2 = np.ones(len(t))*0.0
    F2[:] = 0
    F2 = 3*np.sin(1*t) + 2*np.sin(3*t) 
    # F2[0:100] = 6
    # F2[100:125] = 9
    # F2[126:]=0
    sho2res = sho.perform_simulation(t, y0=y0, Fs=F2)
    sho2res.plot_results()
# #%%

    # Initial Conditions
    x1_0 = 2
    v1_0 = -1
    y0 =[x1_0, v1_0]

    # Force excitation
    F2 = np.ones(len(t))*0.0

    sho3res = sho.perform_simulation(t, y0=y0, Fs=F2)
    sho3res.plot_results()

    sho1res.create_animated_plot()
#%%
    plt.show()
# %%


