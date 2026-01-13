
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Instagram(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-instagram'], 'items': [{'rect': {'width': '20', 'height': '20', 'x': '2', 'y': '2', 'rx': '5', 'ry': '5'}}, {'path': {'d': 'M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z'}}, {'line': {'x1': '17.5', 'x2': '17.51', 'y1': '6.5', 'y2': '6.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
