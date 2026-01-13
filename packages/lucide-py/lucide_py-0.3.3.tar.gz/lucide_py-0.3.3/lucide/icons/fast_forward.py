
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FastForward(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-fast-forward'], 'items': [{'path': {'d': 'M12 6a2 2 0 0 1 3.414-1.414l6 6a2 2 0 0 1 0 2.828l-6 6A2 2 0 0 1 12 18z'}}, {'path': {'d': 'M2 6a2 2 0 0 1 3.414-1.414l6 6a2 2 0 0 1 0 2.828l-6 6A2 2 0 0 1 2 18z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
