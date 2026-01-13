
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RectangleVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rectangle-vertical'], 'items': [{'rect': {'width': '12', 'height': '20', 'x': '6', 'y': '2', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
