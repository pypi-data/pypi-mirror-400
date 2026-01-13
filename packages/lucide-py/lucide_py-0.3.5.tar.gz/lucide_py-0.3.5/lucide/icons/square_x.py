
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-x'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2', 'ry': '2'}}, {'path': {'d': 'm15 9-6 6'}}, {'path': {'d': 'm9 9 6 6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
