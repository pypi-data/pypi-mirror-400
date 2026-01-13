
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Underline(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-underline'], 'items': [{'path': {'d': 'M6 4v6a6 6 0 0 0 12 0V4'}}, {'line': {'x1': '4', 'x2': '20', 'y1': '20', 'y2': '20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
