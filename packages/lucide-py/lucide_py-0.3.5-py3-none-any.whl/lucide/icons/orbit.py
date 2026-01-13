
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Orbit(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-orbit'], 'items': [{'path': {'d': 'M20.341 6.484A10 10 0 0 1 10.266 21.85'}}, {'path': {'d': 'M3.659 17.516A10 10 0 0 1 13.74 2.152'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '3'}}, {'circle': {'cx': '19', 'cy': '5', 'r': '2'}}, {'circle': {'cx': '5', 'cy': '19', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
