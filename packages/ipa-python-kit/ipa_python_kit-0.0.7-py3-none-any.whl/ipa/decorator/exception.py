import sys
from functools import wraps
from typing import Callable, Optional, Type, Union

if sys.version_info >= (3, 9):
    from collections.abc import Iterable
else:
    from typing import Iterable

ExceptionType = Union[Type[Exception], Iterable[Type[Exception]]]


def catch(
    includes: Optional[ExceptionType] = None,
    excludes: Optional[ExceptionType] = None,
    on_catch: Optional[Callable[[Exception], None]] = None,
):
    """
    捕获函数执行过程中出现的异常

    Args:
        func: 要包装的函数
        includes: 要包含的异常类型，默认包含所有异常
        excludes: 要排除的异常类型，默认不排除任何异常,优先级高
        on_catch: 捕获异常后的回调函数，默认不执行任何操作
    """

    if includes and not isinstance(includes, Iterable):
        includes = tuple((includes,))
    if excludes and not isinstance(excludes, Iterable):
        excludes = tuple((excludes,))

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if excludes and isinstance(e, tuple(excludes)):
                    raise e
                if includes and not isinstance(e, tuple(includes)):
                    raise e
                if on_catch:
                    on_catch(e)

        return wrapper

    return decorator
