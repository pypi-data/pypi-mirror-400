
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LockOpen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-lock-open'], 'items': [{'rect': {'width': '18', 'height': '11', 'x': '3', 'y': '11', 'rx': '2', 'ry': '2'}}, {'path': {'d': 'M7 11V7a5 5 0 0 1 9.9-1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
