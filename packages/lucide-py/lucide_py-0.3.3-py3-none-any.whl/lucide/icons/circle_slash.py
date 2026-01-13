
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleSlash(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-slash'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'line': {'x1': '9', 'x2': '15', 'y1': '15', 'y2': '9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
