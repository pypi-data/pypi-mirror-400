
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Spline(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-spline'], 'items': [{'circle': {'cx': '19', 'cy': '5', 'r': '2'}}, {'circle': {'cx': '5', 'cy': '19', 'r': '2'}}, {'path': {'d': 'M5 17A12 12 0 0 1 17 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
