
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowUpRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-up-right'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M8 8h8v8'}}, {'path': {'d': 'm8 16 8-8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
