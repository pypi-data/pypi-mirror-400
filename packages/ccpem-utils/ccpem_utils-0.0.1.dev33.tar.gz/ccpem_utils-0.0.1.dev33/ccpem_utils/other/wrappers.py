from functools import wraps


def inplace(attribute):
    raise NotImplementedError("This decorator is not yet implemented")

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, inplace=False, **kwargs):
            result = func(self, *args, **kwargs)
            if inplace:
                if isinstance(result, tuple):
                    setattr(self, attribute, result[0])
                    return result[1:]
                else:
                    setattr(self, attribute, result)
            else:
                return result

        return wrapper

    return decorator
