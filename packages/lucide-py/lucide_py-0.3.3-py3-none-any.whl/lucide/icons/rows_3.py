
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Rows3(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rows-3'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M21 9H3'}}, {'path': {'d': 'M21 15H3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
