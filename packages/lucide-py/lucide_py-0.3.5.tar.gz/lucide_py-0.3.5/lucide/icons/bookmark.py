
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bookmark(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bookmark'], 'items': [{'path': {'d': 'm19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
