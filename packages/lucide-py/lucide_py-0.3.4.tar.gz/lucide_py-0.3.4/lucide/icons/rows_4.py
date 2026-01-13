
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Rows4(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rows-4'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M21 7.5H3'}}, {'path': {'d': 'M21 12H3'}}, {'path': {'d': 'M21 16.5H3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
