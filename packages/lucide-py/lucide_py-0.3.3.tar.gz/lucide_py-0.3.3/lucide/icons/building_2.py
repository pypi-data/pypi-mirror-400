
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Building2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-building-2'], 'items': [{'path': {'d': 'M10 12h4'}}, {'path': {'d': 'M10 8h4'}}, {'path': {'d': 'M14 21v-3a2 2 0 0 0-4 0v3'}}, {'path': {'d': 'M6 10H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2'}}, {'path': {'d': 'M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
