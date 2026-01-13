
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Link2Off(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-link-2-off'], 'items': [{'path': {'d': 'M9 17H7A5 5 0 0 1 7 7'}}, {'path': {'d': 'M15 7h2a5 5 0 0 1 4 8'}}, {'line': {'x1': '8', 'x2': '12', 'y1': '12', 'y2': '12'}}, {'line': {'x1': '2', 'x2': '22', 'y1': '2', 'y2': '22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
