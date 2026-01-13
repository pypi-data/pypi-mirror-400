
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Tablet(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tablet'], 'items': [{'rect': {'width': '16', 'height': '20', 'x': '4', 'y': '2', 'rx': '2', 'ry': '2'}}, {'line': {'x1': '12', 'x2': '12.01', 'y1': '18', 'y2': '18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
