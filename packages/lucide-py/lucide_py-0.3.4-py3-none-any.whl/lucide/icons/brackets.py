
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Brackets(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-brackets'], 'items': [{'path': {'d': 'M16 3h3a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-3'}}, {'path': {'d': 'M8 21H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
