
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowDownRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-down-right'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'm8 8 8 8'}}, {'path': {'d': 'M16 8v8H8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
