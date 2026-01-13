
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Meh(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-meh'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'line': {'x1': '8', 'x2': '16', 'y1': '15', 'y2': '15'}}, {'line': {'x1': '9', 'x2': '9.01', 'y1': '9', 'y2': '9'}}, {'line': {'x1': '15', 'x2': '15.01', 'y1': '9', 'y2': '9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
