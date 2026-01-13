
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Compass(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-compass'], 'items': [{'path': {'d': 'm16.24 7.76-1.804 5.411a2 2 0 0 1-1.265 1.265L7.76 16.24l1.804-5.411a2 2 0 0 1 1.265-1.265z'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
