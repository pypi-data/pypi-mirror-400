
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessageCircleX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-message-circle-x'], 'items': [{'path': {'d': 'M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719'}}, {'path': {'d': 'm15 9-6 6'}}, {'path': {'d': 'm9 9 6 6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
