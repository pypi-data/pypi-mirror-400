from inspect import signature

from .depends import Depends


def inject(func):
    sig = signature(func)
    params = sig.parameters

    def wrapper(*args, **kwargs):
        for name, param in params.items():
            if isinstance(param.default, Depends):
                if param.default.dependency:
                    kwargs[name] = param.default()
                else:
                    kwargs[name] = Depends(param.annotation)()
        return func(*args, **kwargs)

    return wrapper
