
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RectangleHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rectangle-horizontal'], 'items': [{'rect': {'width': '20', 'height': '12', 'x': '2', 'y': '6', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
