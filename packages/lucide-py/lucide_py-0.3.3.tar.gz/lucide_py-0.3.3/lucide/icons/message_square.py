
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessageSquare(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-message-square'], 'items': [{'path': {'d': 'M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
