
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Server(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-server'], 'items': [{'rect': {'width': '20', 'height': '8', 'x': '2', 'y': '2', 'rx': '2', 'ry': '2'}}, {'rect': {'width': '20', 'height': '8', 'x': '2', 'y': '14', 'rx': '2', 'ry': '2'}}, {'line': {'x1': '6', 'x2': '6.01', 'y1': '6', 'y2': '6'}}, {'line': {'x1': '6', 'x2': '6.01', 'y1': '18', 'y2': '18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
