
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Tally1(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tally-1'], 'items': [{'path': {'d': 'M4 4v16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
