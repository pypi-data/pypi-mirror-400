
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowUpLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-up-left'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M8 16V8h8'}}, {'path': {'d': 'M16 16 8 8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
