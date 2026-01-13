
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareChevronRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-chevron-right'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'm10 8 4 4-4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
