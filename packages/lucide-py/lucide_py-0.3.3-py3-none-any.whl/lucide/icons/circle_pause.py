
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CirclePause(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-pause'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'line': {'x1': '10', 'x2': '10', 'y1': '15', 'y2': '9'}}, {'line': {'x1': '14', 'x2': '14', 'y1': '15', 'y2': '9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
