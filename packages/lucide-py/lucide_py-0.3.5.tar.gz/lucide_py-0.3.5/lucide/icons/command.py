
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Command(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-command'], 'items': [{'path': {'d': 'M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
