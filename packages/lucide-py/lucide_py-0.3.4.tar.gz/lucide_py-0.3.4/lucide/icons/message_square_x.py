
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessageSquareX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-message-square-x'], 'items': [{'path': {'d': 'M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z'}}, {'path': {'d': 'm14.5 8.5-5 5'}}, {'path': {'d': 'm9.5 8.5 5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
