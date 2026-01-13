
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Tally3(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tally-3'], 'items': [{'path': {'d': 'M4 4v16'}}, {'path': {'d': 'M9 4v16'}}, {'path': {'d': 'M14 4v16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
