
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Sheet(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-sheet'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2', 'ry': '2'}}, {'line': {'x1': '3', 'x2': '21', 'y1': '9', 'y2': '9'}}, {'line': {'x1': '3', 'x2': '21', 'y1': '15', 'y2': '15'}}, {'line': {'x1': '9', 'x2': '9', 'y1': '9', 'y2': '21'}}, {'line': {'x1': '15', 'x2': '15', 'y1': '9', 'y2': '21'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
