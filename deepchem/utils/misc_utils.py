"""
Utilities for miscellaneous tasks.
"""
from typing import Union
import scipy
try:
    import torch
except:
    pass


def gaussian_integration(
        n: int, alpha: Union[float,
                             torch.Tensor]) -> Union[float, torch.Tensor]:
    """Performs the gaussian integration.

    Examples
    --------
    >>> gaussian_int(5, 1.0)
    1.0

    Parameters
    ----------
    n: int
        The order of the integral
    alpha: Union[float, torch.Tensor]
        The parameter of the gaussian

    Returns
    -------
    Union[float, torch.Tensor]
        The value of the integral

    """
    n1 = (n + 1) * 0.5
    return scipy.special.gamma(n1) / (2 * alpha**n1)


def indent(s, nspace):
    """Gives indentation of the second line and next lines.
    It is used to format the string representation of an object.
    Which might be containing multiples objects in it.
    Usage: LinearOperator

    Parameters
    ----------
    s: str
        The string to be indented.
    nspace: int
        The number of spaces to be indented.

    Returns
    -------
    str
        The indented string.

    """
    spaces = " " * nspace
    lines = [spaces + c if i > 0 else c for i, c in enumerate(s.split("\n"))]
    return "\n".join(lines)


def shape2str(shape):
    """Convert the shape to string representation.
    It also nicely formats the shape to be readable.

    Parameters
    ----------
    shape: Sequence[int]
        The shape to be converted to string representation.

    Returns
    -------
    str
        The string representation of the shape.

    """
    return "(%s)" % (", ".join([str(s) for s in shape]))
