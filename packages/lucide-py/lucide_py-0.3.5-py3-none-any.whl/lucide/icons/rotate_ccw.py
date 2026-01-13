
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RotateCcw(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rotate-ccw'], 'items': [{'path': {'d': 'M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8'}}, {'path': {'d': 'M3 3v5h5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
