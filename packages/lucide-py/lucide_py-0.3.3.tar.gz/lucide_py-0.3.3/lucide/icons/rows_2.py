
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Rows2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rows-2'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M3 12h18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
