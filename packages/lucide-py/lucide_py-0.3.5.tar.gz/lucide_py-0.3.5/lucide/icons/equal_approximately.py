
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def EqualApproximately(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-equal-approximately'], 'items': [{'path': {'d': 'M5 15a6.5 6.5 0 0 1 7 0 6.5 6.5 0 0 0 7 0'}}, {'path': {'d': 'M5 9a6.5 6.5 0 0 1 7 0 6.5 6.5 0 0 0 7 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
