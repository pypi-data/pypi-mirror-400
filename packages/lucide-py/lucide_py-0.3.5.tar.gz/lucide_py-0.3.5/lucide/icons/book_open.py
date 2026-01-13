
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BookOpen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-book-open'], 'items': [{'path': {'d': 'M12 7v14'}}, {'path': {'d': 'M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
