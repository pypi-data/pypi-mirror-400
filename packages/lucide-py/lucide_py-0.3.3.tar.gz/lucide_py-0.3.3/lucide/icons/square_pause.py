
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquarePause(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-pause'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'line': {'x1': '10', 'x2': '10', 'y1': '15', 'y2': '9'}}, {'line': {'x1': '14', 'x2': '14', 'y1': '15', 'y2': '9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
