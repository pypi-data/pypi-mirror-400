
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def X(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-x'], 'items': [{'path': {'d': 'M18 6 6 18'}}, {'path': {'d': 'm6 6 12 12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
