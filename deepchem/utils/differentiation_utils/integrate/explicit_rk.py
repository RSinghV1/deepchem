from typing import List, Callable, Sequence, NamedTuple, Union
import torch


# list of tableaus
class _Tableau(NamedTuple):
    """To specify a particular method, one needs to provide the integer s
    (the number of stages), and the coefficients a[i,j] (for 1 ≤ j < i ≤ s),
    b[i] (for i = 1, 2, ..., s) and c[i] (for i = 2, 3, ..., s). The matrix
    [aij] is called the Runge–Kutta matrix, while the b[i] and c[i] are known
    as the weights and the nodes. These data are usually arranged in a
    mnemonic device, known as a Butcher tableau (after John C. Butcher):

    Attributes
    ----------
    c: List[float]
        The nodes
    b: List[float]
        The weights
    a: List[List[float]]
        The Runge-Kutta matrix

    """
    c: List[float]
    b: List[float]
    a: List[List[float]]

rk4_tableau = _Tableau(
    c=[0.0, 0.5, 0.5, 1.0],
    b=[1 / 6., 1 / 3., 1 / 3., 1 / 6.],
    a=[[0.0, 0.0, 0.0, 0.0],
       [0.5, 0.0, 0.0, 0.0],
       [0.0, 0.5, 0.0, 0.0],
       [0.0, 0.0, 1.0, 0.0]]
)
rk38_tableau = _Tableau(
    c=[0.0, 1 / 3, 2 / 3, 1.0],
    b=[1 / 8, 3 / 8, 3 / 8, 1 / 8],
    a=[[0.0, 0.0, 0.0, 0.0],
       [1 / 3, 0.0, 0.0, 0.0],
       [-1 / 3, 1.0, 0.0, 0.0],
       [1.0, -1.0, 1.0, 0.0]]
)
fwd_euler_tableau = _Tableau(
    c=[0.0],
    b=[1.0],
    a=[[0.0]]
)

def explicit_rk(tableau: _Tableau,
                fcn: Callable[..., torch.Tensor], t: torch.Tensor, y0: torch.Tensor,
                params: Sequence[torch.Tensor]):
    """The family of explicit Runge–Kutta methods is a generalization
    of the RK4 method mentioned above.

    Parameters
    ----------
    fcn: callable dy/dt = fcn(t, y, *params)
        The function to be integrated. It should produce output of list of
        tensors following the shapes of tuple `y`. `t` should be a single element.
    t: torch.Tensor (nt,)
        The integrated times
    y0: list of torch.Tensor (*ny)
        The list of initial values
    params: list
        List of any other parameters
    **kwargs: dict
        Any other keyword arguments

    Returns
    -------
    yt: list of torch.Tensor (nt,*ny)
        The value of `y` at the given time `t`

    References
    ----------
    [1].. https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods#Explicit_Runge.E2.80.93Kutta_methods

    """
    c = tableau.c
    a = tableau.a
    b = tableau.b
    s = len(c)
    nt = len(t)
    dtype = t.dtype
    device = t.device

    # set up the results list
    yt_lst: List[torch.Tensor] = []
    yt_lst.append(y0)
    y = yt_lst[-1]
    for i in range(nt - 1):
        t0 = t[i]
        t1 = t[i + 1]
        h = t1 - t0
        ks: List[torch.Tensor] = []
        ksum: Union[float, torch.Tensor] = 0.0
        for j in range(s):
            if j == 0:
                k = fcn(y, t0, params)
            else:
                ak: Union[float, torch.Tensor] = 0.0
                aj = a[j]
                for m in range(j):
                    ak = aj[m] * ks[m] + ak
                k = fcn(h * ak + y, t0 + c[j] * h, params)
            ks.append(k)
            ksum = ksum + b[j] * k
        y = h * ksum + y
        yt_lst.append(y)
    yt = torch.stack(yt_lst, dim=0)
    return yt

# list of methods
def rk38_ivp(fcn: Callable[..., torch.Tensor], t: torch.Tensor, y0: torch.Tensor,
             params: Sequence[torch.Tensor], **kwargs):
    """A slight variation of "the" Runge–Kutta method is also due to
    Kutta in 1901 and is called the 3/8-rule.[19] The primary advantage
    this method has is that almost all of the error coefficients are
    smaller than in the popular method, but it requires slightly more
    FLOPs (floating-point operations) per time step.
    
    Parameters
    ----------
    fcn: callable dy/dt = fcn(t, y, *params)
        The function to be integrated. It should produce output of list of
        tensors following the shapes of tuple `y`. `t` should be a single element.
    t: torch.Tensor (nt,)
        The integrated times
    y0: list of torch.Tensor (*ny)
        The list of initial values
    params: list
        List of any other parameters
    **kwargs: dict
        Any other keyword arguments

    Returns
    -------
    yt: list of torch.Tensor (nt,*ny)
        The value of `y` at the given time `t`

    """
    return explicit_rk(rk38_tableau, fcn, t, y0, params)

def fwd_euler_ivp(fcn: Callable[..., torch.Tensor], t: torch.Tensor, y0: torch.Tensor,
                  params: Sequence[torch.Tensor], **kwargs):
    """However, the simplest Runge–Kutta method is the (forward) Euler method,
    given by the formula $y_{n+1} = y_{n} + hf(t_{n}, y_{n}). This is the only
    consistent explicit Runge–Kutta method with one stage.
    
    Parameters
    ----------
    fcn: callable dy/dt = fcn(t, y, *params)
        The function to be integrated. It should produce output of list of
        tensors following the shapes of tuple `y`. `t` should be a single element.
    t: torch.Tensor (nt,)
        The integrated times
    y0: list of torch.Tensor (*ny)
        The list of initial values
    params: list
        List of any other parameters
    **kwargs: dict
        Any other keyword arguments

    Returns
    -------
    yt: list of torch.Tensor (nt,*ny)
        The value of `y` at the given time `t`

    """
    return explicit_rk(fwd_euler_tableau, fcn, t, y0, params)

def rk4_ivp(fcn: Callable[..., torch.Tensor], t: torch.Tensor, y0: torch.Tensor,
            params: Sequence[torch.Tensor], **kwargs):
    """The most commonly used Runge Kutta method to find the solution
    of a differential equation is the RK4 method, i.e., the fourth-order
    Runge-Kutta method. The Runge-Kutta method provides the approximate
    value of y for a given point x. Only the first order ODEs can be
    solved using the Runge Kutta RK4 method.

    Parameters
    ----------
    fcn: callable dy/dt = fcn(t, y, *params)
        The function to be integrated. It should produce output of list of
        tensors following the shapes of tuple `y`. `t` should be a single element.
    t: torch.Tensor (nt,)
        The integrated times
    y0: list of torch.Tensor (*ny)
        The list of initial values
    params: list
        List of any other parameters
    **kwargs: dict
        Any other keyword arguments

    Returns
    -------
    yt: list of torch.Tensor (nt,*ny)
        The value of `y` at the given time `t`

    """
    return explicit_rk(rk4_tableau, fcn, t, y0, params)
