
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleAlert(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-alert'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'line': {'x1': '12', 'x2': '12', 'y1': '8', 'y2': '12'}}, {'line': {'x1': '12', 'x2': '12.01', 'y1': '16', 'y2': '16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
