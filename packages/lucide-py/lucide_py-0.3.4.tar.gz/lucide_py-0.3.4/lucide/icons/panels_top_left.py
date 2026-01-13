
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelsTopLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panels-top-left'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M3 9h18'}}, {'path': {'d': 'M9 21V9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
