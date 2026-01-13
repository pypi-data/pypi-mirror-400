
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Ear(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-ear'], 'items': [{'path': {'d': 'M6 8.5a6.5 6.5 0 1 1 13 0c0 6-6 6-6 10a3.5 3.5 0 1 1-7 0'}}, {'path': {'d': 'M15 8.5a2.5 2.5 0 0 0-5 0v1a2 2 0 1 1 0 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
