
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessageSquareOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-message-square-off'], 'items': [{'path': {'d': 'M19 19H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.7.7 0 0 1 2 21.286V5a2 2 0 0 1 1.184-1.826'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M8.656 3H20a2 2 0 0 1 2 2v11.344'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
