
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Pentagon(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pentagon'], 'items': [{'path': {'d': 'M10.83 2.38a2 2 0 0 1 2.34 0l8 5.74a2 2 0 0 1 .73 2.25l-3.04 9.26a2 2 0 0 1-1.9 1.37H7.04a2 2 0 0 1-1.9-1.37L2.1 10.37a2 2 0 0 1 .73-2.25z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
