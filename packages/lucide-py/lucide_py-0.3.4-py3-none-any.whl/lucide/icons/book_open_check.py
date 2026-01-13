
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BookOpenCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-book-open-check'], 'items': [{'path': {'d': 'M12 21V7'}}, {'path': {'d': 'm16 12 2 2 4-4'}}, {'path': {'d': 'M22 6V4a1 1 0 0 0-1-1h-5a4 4 0 0 0-4 4 4 4 0 0 0-4-4H3a1 1 0 0 0-1 1v13a1 1 0 0 0 1 1h6a3 3 0 0 1 3 3 3 3 0 0 1 3-3h6a1 1 0 0 0 1-1v-1.3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
