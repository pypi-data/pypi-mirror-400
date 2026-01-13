
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleChevronRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-chevron-right'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm10 8 4 4-4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
