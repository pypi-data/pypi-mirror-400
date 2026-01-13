
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Donut(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-donut'], 'items': [{'path': {'d': 'M20.5 10a2.5 2.5 0 0 1-2.4-3H18a2.95 2.95 0 0 1-2.6-4.4 10 10 0 1 0 6.3 7.1c-.3.2-.8.3-1.2.3'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
