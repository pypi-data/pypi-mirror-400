
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Tally5(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tally-5'], 'items': [{'path': {'d': 'M4 4v16'}}, {'path': {'d': 'M9 4v16'}}, {'path': {'d': 'M14 4v16'}}, {'path': {'d': 'M19 4v16'}}, {'path': {'d': 'M22 6 2 18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
