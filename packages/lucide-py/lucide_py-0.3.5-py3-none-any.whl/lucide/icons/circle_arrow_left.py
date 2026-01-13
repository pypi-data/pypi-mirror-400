
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-left'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'm12 8-4 4 4 4'}}, {'path': {'d': 'M16 12H8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
