
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Trello(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-trello'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2', 'ry': '2'}}, {'rect': {'width': '3', 'height': '9', 'x': '7', 'y': '7'}}, {'rect': {'width': '3', 'height': '5', 'x': '14', 'y': '7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
