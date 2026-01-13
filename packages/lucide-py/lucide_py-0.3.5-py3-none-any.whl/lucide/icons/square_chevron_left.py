
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareChevronLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-chevron-left'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'm14 16-4-4 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
