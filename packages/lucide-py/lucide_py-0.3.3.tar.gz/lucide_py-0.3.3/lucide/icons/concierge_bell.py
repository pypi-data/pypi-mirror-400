
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ConciergeBell(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-concierge-bell'], 'items': [{'path': {'d': 'M3 20a1 1 0 0 1-1-1v-1a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v1a1 1 0 0 1-1 1Z'}}, {'path': {'d': 'M20 16a8 8 0 1 0-16 0'}}, {'path': {'d': 'M12 4v4'}}, {'path': {'d': 'M10 4h4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
