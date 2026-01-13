#%% [markdown]
# this is a calculation for tdof systems with matrices M, C, K 

import numpy as np
from np_vmd.misc import convert_harmonic_to_cos, convert_harmonic_to_sin
from np_vmd.sdof_funcs import SDOF_system
from np_vmd.tdof_MCK import TDOF_modal

class MDOFFreeResponseI():
    def __init__(self, mdof_sys: TDOF_modal):
        self.mdof_sys = mdof_sys

    def set_iv(self, x0s:None, dx0s=None):
        """ Set the initial values for the system.

        Parameters:
        x0s (None or array-like): Initial displacements for each degree of freedom.
        dx0s (None or array-like): Initial velocities for each degree of freedom.
        """
        self.x0s = x0s
        self.dx0s = dx0s
        self.r0s = self.mdof_sys.to_modal_cs(self.x0s)
        self.dr0s = self.mdof_sys.to_modal_cs(self.dx0s)

        
    def _set_rfs_hom(self):
        ''' Create response functions for the homogeneous equation
        of the MDOF
        '''
        self.rfs_h = []
        for i in range(self.mdof_sys.dofs):
            x0i = self.r0s[i]
            dx0i = self.dr0s[i]
            wn = self.mdof_sys.wns[i]
            self.rfs_h.append(
                TDOF_modal._gen_modal_d_eq(wn, z=self.mdof_sys.zs[i],x0=x0i, dx0=dx0i)
            )

    def calc_x_hom_response(self, ts):
        ''' returns the numerical values for the homogenous part of the response (transient)
        uses rfs in order to create the numerical response results 
        '''
        self._set_rfs_hom()
        ris = []
        for i in range(self.mdof_sys.dofs):
            ris.append(self.rfs_h[i](ts))
        xs = self.mdof_sys.Smat.dot(np.array(ris))
        return xs



class MDOFGenericResponseI():
    def __init__(self, mdof_sys: TDOF_modal):
        self.mdof_sys = mdof_sys

    # =============== Excitation setup functions ==================
    def set_iv(self, x0s:None, dx0s=None):
        """ Set the initial values for the system.

        Parameters:
        x0s (None or array-like): Initial displacements for each degree of freedom.
        dx0s (None or array-like): Initial velocities for each degree of freedom.
        """
        self.x0s = x0s
        self.dx0s = dx0s
        self.r0s = self.mdof_sys.to_modal_cs(self.x0s)
        self.dr0s = self.mdof_sys.to_modal_cs(self.dx0s)

    def set_excitation(self, B=None, F=None, Fparams:list=None):
        ''' This function sets the excitation parameters.
        # TODO what is B?
        Fparams is a list which contain tuples of the form (F_mag_N, w_F_radps, phi_F_rad)
        '''
        self.mB = np.eye(self.mdof_sys.dofs)  if B is None else B
        self.mF = np.zeros((self.mdof_sys.dofs,1))  if F is None else F
        self.B_tilde = self.mdof_sys.Pmat.T.dot(self.mdof_sys.Linv).dot(self.mB)
        if Fparams is not None:
            assert len(Fparams)==self.mdof_sys.dofs, """shape of Fparams does not agree with M matrix. use (0,0,0) for no forces """ 
            self._f_params = np.array(Fparams)
            
            self.Fs = []
            for Fp in self._f_params:
                self.Fs.append(lambda t: Fp[0]*np.cos(Fp[1]*t + Fp[2]))
        return self.B_tilde

    # =============== Calculation functions ==================
    # -----------modal coordinate systems--------------
    def _set_rfs_hom(self):
        ''' Create response functions for the homogeneous equation
        of the MDOF
        '''
        self.rfs_h = []
        for i in range(self.mdof_sys.dofs):
            x0i = self.r0s[i]
            dx0i = self.dr0s[i]
            wn = self.mdof_sys.wns[i]
            self.rfs_h.append(
                TDOF_modal._gen_modal_d_eq(wn, z=self.mdof_sys.zs[i],x0=x0i, dx0=dx0i)
            )
    # -----------modal coordinate systems--------------
    def calc_x_hom_response(self, ts):
        ''' returns the numerical values for the homogenous part of the response (transient)
        uses rfs in order to create the numerical response results 
        '''
        self._set_rfs_hom()
        ris = []
        for i in range(self.mdof_sys.dofs):
            ris.append(self.rfs_h[i](ts))
        xs = self.mdof_sys.Smat.dot(np.array(ris))
        return xs

    def calc_x_ss_response(self, ts):
        ''' Calculates the steady state response of the system (partial solution)

        # TODO: not complete need to see how to handle convolution integral
        This is the function that creates the 
        '''

        # ris = []

        # for i in range(self._n):
        #     ris.append(self.rfs_ss[i](ts))
        # xs = self.Smat.dot(np.array(ris))
        # return xs
        raise(NotImplementedError())
        pass

    def calc_x_total_response(self, ts:np.ndarray):
        ''' Calculates the total response of a mdof system 

        This is based partially on # https://www.youtube.com/watch?v=sqdd0ja1PXM&t=1s

        Requires:
        - the mass, stiffness and damping matrices
        - setting the initial conditions
        - setting the excitation

        Arguments:
            ts {ndarray} -- tiume vector in seconds
        
        Returns:

        '''

        # ris = []

        # for i in range(self._n):
        #     ris.append(self.rfs_ss[i](ts))
        # xs = self.Smat.dot(np.array(ris))
        # return xs
        raise(NotImplementedError())
        pass
