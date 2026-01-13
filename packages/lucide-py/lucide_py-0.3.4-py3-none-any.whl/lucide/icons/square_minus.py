
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-minus'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M8 12h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
