
#%% [markdown]
#  Goal 
# Is to create a class for the laplace analysies  with sympy
# an example for a two degree of freedom harmonic oscillator using Laplace transforms.
#
# The example that will be provided is in Inman's book 


# # equations of motion

# $\mathbf{M_{mat}}\ddot{\mathbf{x}} + \mathbf{C_{mat}}\dot{\mathbf{x}} + \mathbf{K_{mat}}\mathbf{x} = \mathbf{F}$

#  $\begin{bmatrix} m_1 & 0 \\ 0 & m_2\end{bmatrix}            \cdot \begin{bmatrix}\ddot{x_1} \\ \ddot{x_2} \end{bmatrix} + 
#     \begin{bmatrix} c_1 +c_2 & -c_2 \\ -c_2 & c_2\end{bmatrix} \cdot \begin{bmatrix}\dot{x_1}  \\ \dot{x_2}  \end{bmatrix} +
#     \begin{bmatrix} k_1+k_2 & -k_2 \\ -k_2 & k_2\end{bmatrix}  \cdot \begin{bmatrix} x_1        \\ x_2       \end{bmatrix} =0 $

# or

# $\begin{cases} m_1\ddot{x_1} + (c_1+c_2)\dot{x_1} - c_2\dot{x_2} + (k_1+k_2)x_1 - k_2x_2 = 0 \\
#        m_1\ddot{x_1} + c_2(\dot{x_2} - \dot{x_1})  + k_2( x_2 - x_1 ) = 0 \end{cases}$


#%% [imports]
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
print('sympy version: ', sp.__version__)

t, s = sp.symbols('t s')
#%%
class LaplaceMdofSolver():
    """ Laplace solver for MDOF systems

    used for 2nd order differential equations
    """
    _n = 2
    def __init__(self, des_list:list, vars:list, ) -> None:
        """initialises the solver class

        Args:
            des_list (list): differential equation list
            vars (list): sympy variable list
        """
        self._des_list = des_list
        self._vars = vars
        self._n = len(vars)
        assert len(vars) >0, "number of variables must be greater than zero"
        assert isinstance(vars[0], sp.FunctionClass), "variables must be sympy functions"
        assert len(vars) == len(des_list), "number of variables and equations must be the same"


        self._vars_laplace  = [sp.laplace_transform(var(t), t, s, noconds=True) for var in self._vars]
        
    
    def initial_conditions(self, x0s:list=None, v0s:list=None) -> None:
        """ set initial conditions
        """ 
        if x0s is None:
            x0s = [0]*self._n
        if v0s is None:
            v0s = [0]*self._n
        assert len(x0s) == self._n, "number of initial conditions must be the same as the number of variables"
        assert len(v0s) == self._n, "number of initial conditions must be the same as the number of variables"

        x0s_dict = {self._vars[i](0):x0s[i] for i in range(len(x0s))}
        v0s_dict = {self._vars[i](t).diff(t).subs(t, 0):v0s[i] for i in range(len(v0s))}
        # merge dicts
        self._initial_conditions = {**x0s_dict, **v0s_dict}
    
    def process(self):
        """ process the equations
        """
        # Laplace transform
        self._lap_eqs = [sp.laplace_transform(eq.lhs - eq.rhs, t, s, noconds=True) for eq in self._des_list]
        # Solve the linear system
        self._lap_eqs2 = [lap_eq.subs(self._initial_conditions) for lap_eq in self._lap_eqs]
        self._laplace_sols = sp.linsolve(self._lap_eqs2, *self._vars_laplace   ) # self._vars_laplace[0], self._vars_laplace[1] )
        # Extracting the solutions
        self._sols = [sp.inverse_laplace_transform(eq, s, t)  for eq in self._laplace_sols.args[0]]
        # substitute initial conditions
        self._sols = [sol.subs(self._initial_conditions) for sol in self._sols]

#%%

if __name__ == "__main__":
    # Define constants and variables
    m1, m2, c1, c2, k1, k2 = 9, 1, 0, 0, 24, 3
    F1 = 0
    w1_exc = 2*np.pi*3
    # x1, x2 = sp.symbols('x1 x2', cls=sp.Function) # alternative syntax
    x1 = sp.Function('x1')
    x2 = sp.Function('x2')
    # Differential equations
    des = []
    diff_eq1 = sp.Eq(x1(t).diff(t, 2) + 1/m1*( (c1+c2)*x1(t).diff(t) - c2*x2(t).diff(t)  + (k1+k2)*x1(t) - k2*x2(t) - F1*sp.sin(w1_exc*t)), 0)
    diff_eq2 = sp.Eq(x2(t).diff(t, 2) + 1/m2*(    -c2 *x1(t).diff(t) + c2*x2(t).diff(t)  -      k2*x1(t) + k2*x2(t)), 0)
    des.append(diff_eq1)
    des.append(diff_eq2)
    # Initial conditions
    x0s =[1,1/3]
    v0s =[0,0]
                
    #%%
    lp = LaplaceMdofSolver(des_list = des , vars = [x1, x2])
    lp.initial_conditions(x0s, v0s)
    #%%
    lp.process()

    #%%
    # Extracting the solutions
    x1_solution = lp._sols[0].subs(lp._initial_conditions)
    x2_solution = lp._sols[1].subs(lp._initial_conditions)
    #%%
    # Plotting the solutions
    p = sp.plot(x1_solution, x2_solution, (t, 0, 10), show=False)
    p[0].line_color = 'blue'
    p[1].line_color = 'red'
    p.title = 'Solutions of x1(t) and x2(t)'
    p.xlabel = 't'
    p.ylabel = 'Functions'
    # p.legend = True
    p.show()

    # %%
