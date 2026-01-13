
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Scooter(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-scooter'], 'items': [{'path': {'d': 'M21 4h-3.5l2 11.05'}}, {'path': {'d': 'M6.95 17h5.142c.523 0 .95-.406 1.063-.916a6.5 6.5 0 0 1 5.345-5.009'}}, {'circle': {'cx': '19.5', 'cy': '17.5', 'r': '2.5'}}, {'circle': {'cx': '4.5', 'cy': '17.5', 'r': '2.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
