
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDown01(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-0-1'], 'items': [{'path': {'d': 'm3 16 4 4 4-4'}}, {'path': {'d': 'M7 20V4'}}, {'rect': {'x': '15', 'y': '4', 'width': '4', 'height': '6', 'ry': '2'}}, {'path': {'d': 'M17 20v-6h-2'}}, {'path': {'d': 'M15 20h4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
