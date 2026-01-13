
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleChevronUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-chevron-up'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm8 14 4-4 4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
