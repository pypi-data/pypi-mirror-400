
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessageCircleCode(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-message-circle-code'], 'items': [{'path': {'d': 'm10 9-3 3 3 3'}}, {'path': {'d': 'm14 15 3-3-3-3'}}, {'path': {'d': 'M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
