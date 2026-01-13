
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareActivity(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-activity'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M17 12h-2l-2 5-2-10-2 5H7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
