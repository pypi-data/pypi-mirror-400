
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleChevronDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-chevron-down'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm16 10-4 4-4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
