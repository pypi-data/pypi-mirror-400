
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LifeBuoy(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-life-buoy'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm4.93 4.93 4.24 4.24'}}, {'path': {'d': 'm14.83 9.17 4.24-4.24'}}, {'path': {'d': 'm14.83 14.83 4.24 4.24'}}, {'path': {'d': 'm9.17 14.83-4.24 4.24'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
