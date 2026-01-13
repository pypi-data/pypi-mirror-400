
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Volume(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-volume'], 'items': [{'path': {'d': 'M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
