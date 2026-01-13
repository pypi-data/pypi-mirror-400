
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MountainSnow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mountain-snow'], 'items': [{'path': {'d': 'm8 3 4 8 5-5 5 15H2L8 3z'}}, {'path': {'d': 'M4.14 15.08c2.62-1.57 5.24-1.43 7.86.42 2.74 1.94 5.49 2 8.23.19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
