
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bold(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bold'], 'items': [{'path': {'d': 'M6 12h9a4 4 0 0 1 0 8H7a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h7a4 4 0 0 1 0 8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
