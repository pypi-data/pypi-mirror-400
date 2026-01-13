
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Lasso(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-lasso'], 'items': [{'path': {'d': 'M3.704 14.467A10 8 0 0 1 2 10a10 8 0 0 1 20 0 10 8 0 0 1-10 8 10 8 0 0 1-5.181-1.158'}}, {'path': {'d': 'M7 22a5 5 0 0 1-2-3.994'}}, {'circle': {'cx': '5', 'cy': '16', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
