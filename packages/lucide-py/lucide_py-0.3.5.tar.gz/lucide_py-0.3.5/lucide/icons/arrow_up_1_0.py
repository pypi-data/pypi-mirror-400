
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUp10(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-1-0'], 'items': [{'path': {'d': 'm3 8 4-4 4 4'}}, {'path': {'d': 'M7 4v16'}}, {'path': {'d': 'M17 10V4h-2'}}, {'path': {'d': 'M15 10h4'}}, {'rect': {'x': '15', 'y': '14', 'width': '4', 'height': '6', 'ry': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
