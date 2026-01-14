from fastapi import Depends
from functools import wraps
from pygen_modules.auth.jwthandler import verify_token


def secure_get(router, path, *args, **kwargs):
    def decorator(func):

        @router.get(path, *args, **kwargs)
        @wraps(func)
        async def wrapper(*f_args, user=Depends(verify_token), **f_kwargs):
            return await func(*f_args, user=user, **f_kwargs)

        return wrapper

    return decorator


def secure_post(router, path, *args, **kwargs):
    def decorator(func):
        return router.post(path, *args, **kwargs, dependencies=[Depends(verify_token)])(
            func
        )

    return decorator


def secure_patch(router, path, *args, **kwargs):
    def decorator(func):
        return router.patch(
            path, *args, **kwargs, dependencies=[Depends(verify_token)]
        )(func)

    return decorator


def secure_delete(router, path, *args, **kwargs):
    def decorator(func):
        return router.delete(
            path, *args, **kwargs, dependencies=[Depends(verify_token)]
        )(func)

    return decorator
