
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Waypoints(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-waypoints'], 'items': [{'circle': {'cx': '12', 'cy': '4.5', 'r': '2.5'}}, {'path': {'d': 'm10.2 6.3-3.9 3.9'}}, {'circle': {'cx': '4.5', 'cy': '12', 'r': '2.5'}}, {'path': {'d': 'M7 12h10'}}, {'circle': {'cx': '19.5', 'cy': '12', 'r': '2.5'}}, {'path': {'d': 'm13.8 17.7 3.9-3.9'}}, {'circle': {'cx': '12', 'cy': '19.5', 'r': '2.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
