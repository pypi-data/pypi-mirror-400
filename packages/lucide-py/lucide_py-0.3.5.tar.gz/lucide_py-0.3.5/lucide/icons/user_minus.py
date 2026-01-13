
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-minus'], 'items': [{'path': {'d': 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'}}, {'circle': {'cx': '9', 'cy': '7', 'r': '4'}}, {'line': {'x1': '22', 'x2': '16', 'y1': '11', 'y2': '11'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
