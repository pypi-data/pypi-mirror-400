
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Cloud(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cloud'], 'items': [{'path': {'d': 'M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
