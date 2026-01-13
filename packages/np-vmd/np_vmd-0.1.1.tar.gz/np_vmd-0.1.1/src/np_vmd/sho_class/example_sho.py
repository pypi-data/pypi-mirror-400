# this py file showcases the SHOClass

from np_vmd.sho_class.SHO_sdof_class import SHOSdofSolver
import numpy as np
import matplotlib.pyplot as plt

#%% simple animation of a mass. 

plt.rcParams["font.size"] = "15"

#%%
if __name__ == "__main__":
    # system definition
    m1= 1
    c1 = 0.5
    k = 3



    sho = SHOSdofSolver(m=m1, c=c1, k=k)
#%%
    # set time
    niter = 1001
    t = np.linspace(0,40,niter)

#%%
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
    sho1_res = sho.perform_simulation(t, y0=y0, Fs=F2, desc="Full")
    sho1_res.plot_results()

#%% 
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
    sho2_res = sho.perform_simulation(t, y0=y0, Fs=F2, desc="Zero initial conditions")
    sho2_res.plot_results()
#%%
    # Initial Conditions
    x1_0 = 2
    v1_0 = -1
    y0 =[x1_0, v1_0]

    # Force excitation
    F2 = np.ones(len(t))*0.0

    sho3_res = sho.perform_simulation(t, y0=y0, Fs=F2, desc="Zero Input (F)")
    sho3_res.plot_results()
    sho3_res.create_animated_plot(xlim =(-3, 3), ylim = [-3, 8])
    plt.show()
# %%


