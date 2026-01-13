
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Anchor(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-anchor'], 'items': [{'path': {'d': 'M12 6v16'}}, {'path': {'d': 'm19 13 2-1a9 9 0 0 1-18 0l2 1'}}, {'path': {'d': 'M9 11h6'}}, {'circle': {'cx': '12', 'cy': '4', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
