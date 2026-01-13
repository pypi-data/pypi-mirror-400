import functools
import types
from typing import *

from identityfunction import identityfunction

__all__ = ["funccomp"]


def funccomp(
    *callables: Callable,
) -> types.FunctionType:

    if 0 == len(callables):
        return identityfunction

    @functools.wraps(callables[0])
    def ans(*args: Any, **kwargs: Any) -> Any:
        ans_: Any
        func: Callable
        ans_ = callables[-1](*args, **kwargs)
        for func in callables[-2::-1]:
            ans_ = func(ans_)
        return ans_

    return ans
