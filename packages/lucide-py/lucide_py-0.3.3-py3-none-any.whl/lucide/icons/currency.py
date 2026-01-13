
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Currency(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-currency'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '8'}}, {'line': {'x1': '3', 'x2': '6', 'y1': '3', 'y2': '6'}}, {'line': {'x1': '21', 'x2': '18', 'y1': '3', 'y2': '6'}}, {'line': {'x1': '3', 'x2': '6', 'y1': '21', 'y2': '18'}}, {'line': {'x1': '21', 'x2': '18', 'y1': '21', 'y2': '18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
