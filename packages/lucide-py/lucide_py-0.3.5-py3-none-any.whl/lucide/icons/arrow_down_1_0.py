
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDown10(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-1-0'], 'items': [{'path': {'d': 'm3 16 4 4 4-4'}}, {'path': {'d': 'M7 20V4'}}, {'path': {'d': 'M17 10V4h-2'}}, {'path': {'d': 'M15 10h4'}}, {'rect': {'x': '15', 'y': '14', 'width': '4', 'height': '6', 'ry': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
