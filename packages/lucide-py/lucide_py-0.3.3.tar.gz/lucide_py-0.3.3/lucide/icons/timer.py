
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Timer(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-timer'], 'items': [{'line': {'x1': '10', 'x2': '14', 'y1': '2', 'y2': '2'}}, {'line': {'x1': '12', 'x2': '15', 'y1': '14', 'y2': '11'}}, {'circle': {'cx': '12', 'cy': '14', 'r': '8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
