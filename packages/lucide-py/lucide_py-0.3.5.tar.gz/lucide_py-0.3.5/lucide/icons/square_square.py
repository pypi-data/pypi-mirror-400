
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareSquare(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-square'], 'items': [{'rect': {'x': '3', 'y': '3', 'width': '18', 'height': '18', 'rx': '2'}}, {'rect': {'x': '8', 'y': '8', 'width': '8', 'height': '8', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
