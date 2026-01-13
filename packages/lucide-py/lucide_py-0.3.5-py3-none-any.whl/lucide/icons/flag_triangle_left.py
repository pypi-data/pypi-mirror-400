
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlagTriangleLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flag-triangle-left'], 'items': [{'path': {'d': 'M18 22V2.8a.8.8 0 0 0-1.17-.71L5.45 7.78a.8.8 0 0 0 0 1.44L18 15.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
