
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Tent(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tent'], 'items': [{'path': {'d': 'M3.5 21 14 3'}}, {'path': {'d': 'M20.5 21 10 3'}}, {'path': {'d': 'M15.5 21 12 15l-3.5 6'}}, {'path': {'d': 'M2 21h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
