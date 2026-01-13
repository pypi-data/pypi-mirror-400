
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BadgeInfo(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-badge-info'], 'items': [{'path': {'d': 'M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76Z'}}, {'line': {'x1': '12', 'x2': '12', 'y1': '16', 'y2': '12'}}, {'line': {'x1': '12', 'x2': '12.01', 'y1': '8', 'y2': '8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
