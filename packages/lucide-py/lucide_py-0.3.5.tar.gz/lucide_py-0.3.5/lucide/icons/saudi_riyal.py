
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SaudiRiyal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-saudi-riyal'], 'items': [{'path': {'d': 'm20 19.5-5.5 1.2'}}, {'path': {'d': 'M14.5 4v11.22a1 1 0 0 0 1.242.97L20 15.2'}}, {'path': {'d': 'm2.978 19.351 5.549-1.363A2 2 0 0 0 10 16V2'}}, {'path': {'d': 'M20 10 4 13.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
