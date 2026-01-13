
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PhilippinePeso(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-philippine-peso'], 'items': [{'path': {'d': 'M20 11H4'}}, {'path': {'d': 'M20 7H4'}}, {'path': {'d': 'M7 21V4a1 1 0 0 1 1-1h4a1 1 0 0 1 0 12H7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
