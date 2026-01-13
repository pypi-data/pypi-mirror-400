
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerLeftUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-left-up'], 'items': [{'path': {'d': 'M14 9 9 4 4 9'}}, {'path': {'d': 'M20 20h-7a4 4 0 0 1-4-4V4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
