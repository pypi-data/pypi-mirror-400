
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Handbag(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-handbag'], 'items': [{'path': {'d': 'M2.048 18.566A2 2 0 0 0 4 21h16a2 2 0 0 0 1.952-2.434l-2-9A2 2 0 0 0 18 8H6a2 2 0 0 0-1.952 1.566z'}}, {'path': {'d': 'M8 11V6a4 4 0 0 1 8 0v5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
