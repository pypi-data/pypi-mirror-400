
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FileStack(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-file-stack'], 'items': [{'path': {'d': 'M11 21a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-8a1 1 0 0 1 1-1'}}, {'path': {'d': 'M16 16a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1'}}, {'path': {'d': 'M21 6a2 2 0 0 0-.586-1.414l-2-2A2 2 0 0 0 17 2h-3a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
