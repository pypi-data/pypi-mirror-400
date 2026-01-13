
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Link2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-link-2'], 'items': [{'path': {'d': 'M9 17H7A5 5 0 0 1 7 7h2'}}, {'path': {'d': 'M15 7h2a5 5 0 1 1 0 10h-2'}}, {'line': {'x1': '8', 'x2': '16', 'y1': '12', 'y2': '12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
