
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessageSquareMore(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-message-square-more'], 'items': [{'path': {'d': 'M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z'}}, {'path': {'d': 'M12 11h.01'}}, {'path': {'d': 'M16 11h.01'}}, {'path': {'d': 'M8 11h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
