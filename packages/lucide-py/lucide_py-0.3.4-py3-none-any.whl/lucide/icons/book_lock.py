
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BookLock(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-book-lock'], 'items': [{'path': {'d': 'M18 6V4a2 2 0 1 0-4 0v2'}}, {'path': {'d': 'M20 15v6a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20'}}, {'path': {'d': 'M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H10'}}, {'rect': {'x': '12', 'y': '6', 'width': '8', 'height': '5', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
