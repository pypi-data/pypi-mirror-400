
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Ban(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-ban'], 'items': [{'path': {'d': 'M4.929 4.929 19.07 19.071'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
