
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Rewind(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rewind'], 'items': [{'path': {'d': 'M12 6a2 2 0 0 0-3.414-1.414l-6 6a2 2 0 0 0 0 2.828l6 6A2 2 0 0 0 12 18z'}}, {'path': {'d': 'M22 6a2 2 0 0 0-3.414-1.414l-6 6a2 2 0 0 0 0 2.828l6 6A2 2 0 0 0 22 18z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
