
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-check'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'm9 12 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
