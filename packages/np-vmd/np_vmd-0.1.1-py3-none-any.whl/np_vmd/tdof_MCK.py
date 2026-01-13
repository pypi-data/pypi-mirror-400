# %% [markdown]
# this is a calculation for tdof systems with matrices M, C, K

import numpy as np
from np_vmd.misc import convert_harmonic_to_cos, convert_harmonic_to_sin
from np_vmd.sdof_funcs import SDOF_system


class TDOF_modal:
    """This class is for the calculation of the response of a TDOF system
    with matrices M, C, K.
    The class is based on the modal analysis of the system.
    """

    _n = 2  # number of degrees of freedom
    _f_params = None  # Force Parameters list of tuples (F_mag_N, w_F_radps, phi_F_rad)

    def __init__(self, M, K, C=None):
        self.mM = M
        self.mK = K
        dims = self.mM.shape
        if len(set(dims)) == 1:
            self._n = self.mM.shape[0]
        else:
            raise ValueError("Size of matrix array not ok")
        self.mC = np.zeros((self._n, self._n)) if C is None else C
        # set up excitation matrices
        # mB* mF
        # mB is the generic case where a force may be shared by moe than one dof
        self.mB = np.zeros((self._n, self._n))
        self.mF = np.zeros((self._n, 1))
        self.__perform_initial_setup()

    def __perform_initial_setup(self):
        """This function performs the initial setup of the system
        It calculates the eigenvalues, eigenvectors, eigenfrequencies, eigenmodes, spectral matrix
        """
        self.M_1ov2 = np.linalg.cholesky(self.mM)
        self.Linv = np.linalg.inv(self.M_1ov2)

        self.Ktilde = self.Linv.dot(self.mK).dot(self.Linv)
        self.Ctilde = self.Linv.dot(self.mC).dot(self.Linv)
        self.ls, self.vs = np.linalg.eig(
            self.Ktilde
        )  # eigenvalues and eigenvectors fro the Ktilde matrix
        self.Pmat = self.vs  # Formulation of the P matrix
        self.wns = np.sqrt(self.ls)  # eigenfrequencies
        self.calc_eigenmodes()  # eigenmodes
        self.Lambda_mat = self.vs.T.dot(self.Ktilde).dot(self.vs)
        self.Smat = self.Linv.dot(self.Pmat)

        # damping
        self.update_damping()

    @property
    def dofs(self) -> int:
        """returns the number of degrees of freedom of the system

        Returns:
            int: number of degrees of freedom
        """
        return self._n

    def get_wns(self):
        return self.wns

    # ======================= Damping =================================
    def update_damping(self, zs=None):
        """sets zs in their **decoupled form** and recalculates the wds

        zs defaults to none which calculates based on the C matrix
        """
        if zs is None:
            self.zs = np.diag(self._calc_C_princ_coord()) / (2 * self.wns)
        else:
            self.zs = zs
        self.wds = self.wns * np.sqrt(1 - self.zs**2)

    def calc_C_from_Z(self, Z=None):
        """Calculates C matrix from the Z matrix of the principal coordinates decoupled equations

        returns a new system with the new C matrix based on the values of the
        damping factor for the decoupled generalised coordinates Z

        TODO: Add test for calc_C_from_Z
        """
        if Z.ndim == 1:
            zn = np.diag(Z * 2 * self.wns)
        elif Z.ndim == 2:
            zn = np.diag(np.diag(Z) * 2 * self.wns)
        else:
            raise ValueError("Z must be 1D or a 2D diagonal matrix")
        C = self.M_1ov2.dot(self.Pmat).dot(zn).dot(self.Pmat.T).dot(self.M_1ov2)
        newsys = TDOF_modal(M=self.mM, K=self.mK, C=C)
        return newsys

    def _calc_C_princ_coord(self):
        """calculate matrix $P^t \tilde{C} P$

        This is damping in the principal coordinates system

        it calculates the damping factor in the principal  coordinates (generalised decoupled).
        """
        return self.Pmat.T.dot(self.Ctilde).dot(self.Pmat)

    # ======================= Eigenvalues and Eigenvectors =================================
    def calc_eigenmodes(self) -> np.ndarray:
        """creates eigenmodes in columns"""
        self.us_nn = np.array(self.M_1ov2.dot(self.vs))  # not necessarily normalised
        us_a = []
        for ui in self.us_nn.T:
            # us_a.append( ui/np.sqrt(np.sum(ui*ui.T)))
            us_a.append(ui / ui[0])
        self.us = np.array(us_a).T
        return self.us_nn

    # ======================= Print results =================================
    def print_eigvectors(self):
        n = len(self.wns)
        print("============ eigen values and eigenvectors =================")
        for i in range(n):
            print(
                "lambda_{}= {:10.3f}, \t eigen vector:{}".format(
                    i + 1, self.ls[i], self.vs[:, i].T
                )
            )

    def print_eigenmodes(self):
        n = len(self.wns)
        print("\n============ eigen Frequencies and eigenmodes =================")
        for i in range(n):
            print(
                "w_{}= {:10.3f}, \t eigen vector:{}".format(
                    i + 1, self.wns[i], self.us[:, i].T
                )
            )

    def print_results(self):
        print("Khat : \n {}".format(self.Ktilde))
        print("Eigenvalues (lambda) :  {}".format(self.ls))
        print("Eigenfrequencies (omega) :  {}".format(self.wns))
        self.print_eigvectors()
        # print("EigenVectors (v) : \n {}".format(self.vs))
        self.print_eigenmodes()
        # print("EigenModes (u) : \n {}".format(self.us))
        print(
            "\n", "*" * 50, "\nSpectral matrix $Lambda$: \n {}".format(self.Lambda_mat)
        )

    # ======================= Excitation =================================
    def set_iv(self, x0s: None, dx0s=None):
        """This functions sets the parameters for the initial conditions of the system

        # TODO: what happens when the excitation have an offset.?
        # In that case in the SDOF, the initial condition should be set to - F/k
        # consider what happens in the principal coordinates.
        """
        self.x0s = x0s
        self.dx0s = dx0s
        self.r0s = np.linalg.inv(self.Smat).dot(self.x0s)
        self.dr0s = np.linalg.inv(self.Smat).dot(self.dx0s)

    # ======================= Excitation =================================
    def to_modal_cs(self, x0s: np.ndarray) -> np.ndarray:
        """converts initial conditions from original to modal coordinates

            $$ [rs]  =  Smat^{-1} * [x0s]$$

        Requires:
        - x0s: (velocity or displacement) in original coordinates

        Returns:
        - r0s: (velocity or displacement) in modal coordinates

        TODO : create tests

        """
        r0s = np.linalg.inv(self.Smat).dot(x0s)
        return r0s

    def to_orig_cs(self, r0s: np.ndarray) -> np.ndarray:
        """converts from original to modal coordinates

            $$ [xs]  =  Smat* [rs]$$

        Requires:
        - r0s: (velocity or displacement) in modal coordinates

        Returns:
        - x0s: (velocity or displacement) in original coordinates

        TODO : create tests
        """
        x0s = self.Smat.dot(r0s)
        return x0s

    @staticmethod
    def _gen_modal_d_eq(wn, z, x0, dx0):
        """generic solution for the homogeneous problem for an underdamped vibration of 1 sdof

        This is used in the principal coordinates to calculate the response in principal coordinates
        TODO: consider using/modifying the SDOF class in order to calculate the lambda.
        # priority: high
        """
        if z < 0:
            raise ValueError("z must be positive")
        if z < 1:
            wd = wn * np.sqrt(1 - z**2)
            A = np.sqrt(x0**2 + ((dx0 + z * wn * x0) / wd) ** 2)
            theta = np.arctan2(wd * x0, dx0 + z * wn * x0)
            r_t = lambda t: A * np.exp(-z * wn * t) * np.sin(wd * t + theta)
            return r_t
        else:
            raise NotImplementedError("z>1 not implemented yet")

    def set_excitation(self, B=None, F=None, Fparams: list = None):
        """This function sets the excitation parameters.
        # TODO what is B?
        Fparams is a list which contain tuples of the form (F_mag_N, w_F_radps, phi_F_rad)
        """
        self.mB = np.eye(self._n) if B is None else B
        self.mF = np.zeros((self._n, 1)) if F is None else F
        self.B_tilde = self.Pmat.T.dot(self.Linv).dot(self.mB)
        if Fparams is not None:
            assert len(Fparams) == self._n, (
                """shape of Fparams does not agree with M matrix. use (0,0,0) for no forces """
            )
            self._f_params = np.array(Fparams)

            self.Fs = []
            for Fp in self._f_params:
                self.Fs.append(lambda t: Fp[0] * np.cos(Fp[1] * t + Fp[2]))
        return self.B_tilde

    def _set_rfs_hom(self):
        """Create response functions for the homogeneous equation
        of the MDOF
        """
        self.rfs_h = []
        for i in range(self._n):
            x0i = self.r0s[i]
            dx0i = self.dr0s[i]
            wn = self.wns[i]
            self.rfs_h.append(
                TDOF_modal._gen_modal_d_eq(wn, z=self.zs[i], x0=x0i, dx0=dx0i)
            )

    def calc_x_hom_response(self, ts):
        """returns the numerical values for the homogenous part of the response (transient)
        uses rfs in order to create the numerical response results
        """
        self._set_rfs_hom()
        ris = []
        for i in range(self._n):
            ris.append(self.rfs_h[i](ts))
        # rotates from modal to original
        xs = self.Smat.dot(np.array(ris))
        return xs

    def calc_x_ss_response(self, ts):
        """Calculates the steady state response of the system (partial solution)

        # TODO: not complete need to see how to handle convolution integral
        This is the function that creates the
        """

        # ris = []

        # for i in range(self._n):
        #     ris.append(self.rfs_ss[i](ts))
        # xs = self.Smat.dot(np.array(ris))
        # return xs
        raise (NotImplementedError())
        pass

    def calc_x_total_response(self, ts: np.ndarray):
        """Calculates the total response of a mdof system

        This is based partially on # https://www.youtube.com/watch?v=sqdd0ja1PXM&t=1s

        Requires:
        - the mass, stiffness and damping matrices
        - setting the initial conditions
        - setting the excitation

        Arguments:
            ts {ndarray} -- tiume vector in seconds

        Returns:

        """

        # ris = []

        # for i in range(self._n):
        #     ris.append(self.rfs_ss[i](ts))
        # xs = self.Smat.dot(np.array(ris))
        # return xs
        raise (NotImplementedError())
        pass


class MDOFFreeResponse:
    def __init__(self, mdof_sys: TDOF_modal):
        self.mdof_sys = mdof_sys

    def set_iv(self, x0s: None, dx0s=None):
        """Set the initial values for the system.

        Parameters:
        x0s (None or array-like): Initial displacements for each degree of freedom.
        dx0s (None or array-like): Initial velocities for each degree of freedom.
        """
        self.x0s = x0s
        self.dx0s = dx0s
        self.r0s = np.linalg.inv(self.mdof_sys.Smat).dot(self.x0s)
        self.dr0s = np.linalg.inv(self.mdof_sys.Smat).dot(self.dx0s)

    def _set_rfs_hom(self):
        """Create response functions for the homogeneous equation
        of the MDOF
        """
        self.rfs_h = []
        for i in range(self.mdof_sys.dofs):
            x0i = self.r0s[i]
            dx0i = self.dr0s[i]
            wn = self.mdof_sys.wns[i]
            self.rfs_h.append(
                TDOF_modal._gen_modal_d_eq(wn, z=self.mdof_sys.zs[i], x0=x0i, dx0=dx0i)
            )

    def calc_x_hom_response(self, ts):
        """returns the numerical values for the homogenous part of the response (transient)
        uses rfs in order to create the numerical response results
        """
        self._set_rfs_hom()
        ris = []
        for i in range(self.mdof_sys.dofs):
            ris.append(self.rfs_h[i](ts))
        xs = self.mdof_sys.Smat.dot(np.array(ris))
        return xs


class MdofForcedResponseSingleExcitation:
    """
    Represents a multi-degree-of-freedom (MDOF) system with a single excitation.

    # TODO rename to MdofForcedResponseSingleExcitation


    Attributes:
        mdof_sys (TDOF_modal): The MDOF system.
        _excitation_node (int): The node at which the excitation is applied.
        _force_mag_N (float): The magnitude of the excitation force.
        _w_exc_radps (float): The angular frequency of the excitation in radians per second.
        _phi_exc_rad (float): The phase angle of the excitation in radians.

    Methods:
        __init__(mdof_sys, node, Fmag, w_exc_radps, phi_exc_rad=0): Initializes the MDOFResponse1Excitation object.
        set_iv(x0s, dx0s): Sets the initial conditions of the system.
        calc_response(): Calculates the response of the MDOF system.
        get_ith_orig_response_params(i, form="AB"): Returns the response parameters for the ith original degree of freedom.
        ith_modal_response(i, update=False): Prints the information for the ith modal coordinate.
        print_all_modal_responses(update=False): Prints the information for each modal coordinate.
        ith_modal_response_str(j, update=False): Returns the response parameters as a string for the jth modal coordinate.
        jth_response_func(j, update=False): Returns the response function for the jth modal coordinate.
    """

    def __init__(
        self,
        mdof_sys: TDOF_modal,
        node: int,
        Fmag: float,
        w_exc_radps: float,
        phi_exc_rad: float = 0,
    ):
        """
        Initializes the MDOFResponse1Excitation object.

        Args:
            mdof_sys (TDOF_modal): The MDOF system.
            node (int): The node at which the excitation is applied.
            Fmag (float): The magnitude of the excitation force.
            w_exc_radps (float): The angular frequency of the excitation in radians per second.
            phi_exc_rad (float, optional): The phase angle of the excitation in radians. Defaults to 0.
        """
        self.mdof_sys = mdof_sys

        # excitation parametes
        self._excitation_node = node
        self._force_mag_N = Fmag
        self._w_exc_radps = w_exc_radps
        self._phi_exc_rad = phi_exc_rad
        self.__create_fparams()

        # calculate Fmagnitude in principal coordinates
        self.Fmag_pc = self.mdof_sys.Smat.T.dot(self.f_params[:, 0])

        # set up initial conditions to zero
        # they should be set by the user
        self.x0s = np.zeros((self.mdof_sys._n, 1))
        self.dx0s = np.zeros((self.mdof_sys._n, 1))
        self.r0s = np.zeros((self.mdof_sys._n, 1))
        self.dr0s = np.zeros((self.mdof_sys._n, 1))

    def set_iv(self, x0s: None, dx0s=None):
        """This functions sets the parameters for the initial conditions of the system"""
        self.x0s = x0s
        self.dx0s = dx0s
        self.r0s = np.linalg.inv(self.mdof_sys.Smat).dot(self.x0s)
        self.dr0s = np.linalg.inv(self.mdof_sys.Smat).dot(self.dx0s)

    @property
    def dofs(self) -> int:
        return self.mdof_sys._n

    def __create_fparams(
        self,
    ):
        """creates a specialised matrix for the force paramaters based on the excitatoin node

        This is a conveniece function to create a matrix of force parameters
        """
        self.f_params = np.zeros((self.mdof_sys._n, 3))
        self.f_params[self._excitation_node, :] = np.array(
            [self._force_mag_N, self._w_exc_radps, self._phi_exc_rad]
        )

    def calc_response(self):
        """
        Calculates the response of the MDOF system.
        """
        self.lst_modal_systems = []
        self.lst_modal_response_params = []
        self.lst_modal_response_funcs = []
        for k in range(self.dofs):
            _modal_sys = SDOF_system.from_wn_mz(
                wn=self.mdof_sys.wns[k], m=1, zeta=self.mdof_sys.zs[k]
            )
            # the rotated initial conditions are placed here
            _modal_resp_parms = _modal_sys.response_params(
                x0=self.r0s[k, 0],
                v0=self.dr0s[k, 0],
                F0=self.Fmag_pc[k],
                w=self._w_exc_radps,
            )
            self.lst_modal_systems.append(_modal_sys)
            self.lst_modal_response_params.append(_modal_resp_parms)
            self.lst_modal_response_funcs.append(_modal_resp_parms.get("x_lambda"))

        # convert back to original coordinates
        # TRANSIENT STATE =============================
        # TODO: this is not complete

        # STEADY STATE =============================
        # x_mags_pc : amplitude of the response in principal coordinates
        self.x_mags_pc = np.diag([x.get("Xss") for x in self.lst_modal_response_params])
        # phis_pc : phase of the response in principal coordinates
        self.phis_pc = [x.get("phi_ss") for x in self.lst_modal_response_params]
        self.angle_2dArray = np.array([[np.cos(x), np.sin(x)] for x in self.phis_pc])
        # xs_mag_orig : amplitude of the response in original coordinates in AB form
        #               (A*cos(w*t+phi)+B*sin(w*t+phi))
        self.xs_ABmag_orig = self.mdof_sys.Smat.dot(self.x_mags_pc).dot(
            self.angle_2dArray
        )

    def get_ith_orig_response_params(self, i: int, form: str = "AB") -> dict:
        """
        Returns the response parameters for the ith original degree of freedom.

        Args:
            i (int): The index of the original degree of freedom.
            form (str, optional): The form of the response parameters. Defaults to "AB".

        Returns:
            dict: The response parameters.
        """
        if form == "AB":
            return self.xs_ABmag_orig[i, :]
        elif form == "x_cos":
            AB = self.xs_ABmag_orig[i, :]
            return convert_harmonic_to_cos(AB[0], AB[1])
        elif form == "x_sin":
            AB = self.xs_ABmag_orig[i, :]
            return convert_harmonic_to_sin(AB[0], AB[1])
        else:
            raise ValueError("form must be 'AB' or 'x_cos' or 'x_sin'")

    def ith_modal_response(self, i: int, update: bool = False) -> str:
        """
        Prints the information for the ith modal coordinate.

        Args:
            i (int): The index of the modal coordinate.
            update (bool, optional): Whether to update the response calculation. Defaults to False.

        Returns:
            str: The information for the ith modal coordinate.
        """
        if update:
            self.calc_response()
        response_str = "\n"
        response_str += f"Principal coordinate: {i + 1}======================\n"
        response_str += f"  - wn: {self.mdof_sys.wns[i]:.3g}\n"
        response_str += f"  - z : {self.mdof_sys.zs[i]:.3g}\n"
        response_str += f"  - F : {self.Fmag_pc[i]:.3g}\n"
        response_str += "  Response:\n"
        response_str += f"      Steady:    Xss: {self.lst_modal_response_params[i].get('Xss'):.3g} phi_ss: {self.lst_modal_response_params[i].get('phi_ss'):.3g}\n"
        response_str += f"      Transient: Xtr: {self.lst_modal_response_params[i].get('X_tra'):.3g} phi_tr: {self.lst_modal_response_params[i].get('phi_tra'):.3g}\n"
        return response_str

    def print_all_modal_responses(self, update: bool = False):
        """
        Prints the information for each modal coordinate.

        Args:
            update (bool, optional): Whether to update the response calculation. Defaults to False.
        """
        if update:
            self.calc_response()
        response_str = "\n"
        for k in range(self.dofs):
            response_str += self.ith_modal_response(k)
        print(response_str)

    def ith_modal_response_str(self, j: int, update: bool = False) -> str:
        """
        Returns the response parameters as a string for the jth modal coordinate.

        Args:
            j (int): The index of the modal coordinate.
            update (bool, optional): Whether to update the response calculation. Defaults to False.

        Returns:
            str: The response parameters as a string.
        """
        if update:
            self.calc_response()
        return self.lst_modal_response_params[j].get("form")

    def jth_response_func(self, j: int, update: bool = False) -> str:
        """
        Returns the response function for the jth modal coordinate.

        Args:
            j (int): The index of the modal coordinate.
            update (bool, optional): Whether to update the response calculation. Defaults to False.

        Returns:
            str: The response function.
        """
        if update:
            self.calc_response()
        res = self.lst_modal_response_params[j]
        Xss, phi_ss = convert_harmonic_to_cos(
            self.xs_ABmag_orig[j, 0], self.xs_ABmag_orig[j, 1]
        )
        X_tra = res.get("X_tra")
        phi_tra = res.get("phi_tra")
        # TODO check this function (the transient part, because only one eigenfrequency is evaluated,
        #      while both should be present in the solution)
        response_func = lambda t: X_tra * np.cos(
            self.mdof_sys.wns[j] * t + phi_tra
        ) + Xss * np.cos(self._w_exc_radps * t + phi_ss)
        return response_func


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # examples 4.1.1. to 4.2.6
    m1, m2 = 9, 1
    k1 = 24
    k2 = 3
    tmck = TDOF_modal(
        np.array([[m1, 0], [0, m2]]), K=np.array([[k1 + k2, -k2], [-k2, k2]])
    )
    tmck.print_results()
    tmck.set_iv(x0s=np.array([[1, 0]]).T, dx0s=np.array([[0, 0]]).T)
    print(tmck.Smat)
    print(tmck.r0s)
    print(tmck.dr0s)
    # ts = np.linspace(0, 5, 1000)
    # plt.plot(tmck.calc_x_response(ts).T , label ='tmck')
    # plt.plot(0.5*(np.cos(np.sqrt(2)*ts) + np.cos(2*ts)) , '.', label ='r1')
    # plt.plot(1.5*(np.cos(np.sqrt(2)*ts) - np.cos(2*ts)) , '.', label ='f2')
    # plt.legend()
    # %%
    # example Inman  4.2.6
    k1 = 10
    k3 = 10
    k2 = 2
    tmck = TDOF_modal(
        np.array([[1, 0], [0, 4]]), K=np.array([[k1 + k2, -k2], [-k2, k2 + k3]])
    )
    tmck.print_results()
    # tmck.cholesky()
    # tmck.calc_Khat()
    # tmck.calc_eigenvalues()
    # tmck.calc_eigenfrequencies()
    # tmck.calc_eigenvectors()
    # tmck.calc_eigenmodes()
    # tmck.calc_spectralMatrix()
    # %%
    # examples 4.1.1. to 4.2.6
    m1, m2 = 9, 1
    k1 = 24
    k2 = 3
    tmck = TDOF_modal(
        np.array([[m1, 0], [0, m2]]), K=np.array([[k1 + k2, -k2], [-k2, k2]])
    )
    tmck.print_results()
    # %%
    tmck.print_eigvectors()
    tmck.print_eigenmodes()
    # %%

    # %%
    # examples 4.3.2
    k1 = 10
    k3 = 10
    k2 = 2
    tmck = TDOF_modal(
        np.array([[1, 0], [0, 4]]), K=np.array([[k1 + k2, -k2], [-k2, k2 + k3]])
    )
    tmck.print_results()
    tmck.set_iv(x0s=np.array([[1, 1]]).T, dx0s=np.array([[0, 0]]).T)
    print(tmck.Smat)
    print(tmck.r0s)
    print(tmck.dr0s)
    ts = np.linspace(0, 5, 1000)
    plt.plot(tmck.calc_x_hom_response(ts).T, label="tmck")
    plt.legend()
    # %%
    # this is an example for an  MDOF (n=3). The TDOF file works just fine.
    m1, m2, m3 = 4, 4, 4
    k1, k2, k3 = 4, 4, 4

    tmck = TDOF_modal(
        np.array([[m1, 0, 0], [0, m2, 0], [0, 0, m3]]),
        K=np.array([[k1 + k2, -k2, 0], [-k2, k2 + k3, -k3], [0, -k3, k3]]),
    )
    tmck.set_iv(x0s=np.array([[1, 0, 0]]).T, dx0s=np.array([[0, 0, 0]]).T)
    ts = np.linspace(0, 5, 1000)
    plt.plot(tmck.calc_x_hom_response(ts).T, label="tmck")
    plt.legend()
    plt.show()
    # %%
    tmck.print_results()
# %%
