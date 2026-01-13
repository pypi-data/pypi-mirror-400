
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareCode(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-code'], 'items': [{'path': {'d': 'm10 9-3 3 3 3'}}, {'path': {'d': 'm14 15 3-3-3-3'}}, {'rect': {'x': '3', 'y': '3', 'width': '18', 'height': '18', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
