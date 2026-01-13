
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def IterationCcw(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-iteration-ccw'], 'items': [{'path': {'d': 'm16 14 4 4-4 4'}}, {'path': {'d': 'M20 10a8 8 0 1 0-8 8h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
