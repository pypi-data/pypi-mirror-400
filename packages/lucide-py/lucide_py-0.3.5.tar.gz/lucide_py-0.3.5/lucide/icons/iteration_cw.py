
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def IterationCw(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-iteration-cw'], 'items': [{'path': {'d': 'M4 10a8 8 0 1 1 8 8H4'}}, {'path': {'d': 'm8 22-4-4 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
