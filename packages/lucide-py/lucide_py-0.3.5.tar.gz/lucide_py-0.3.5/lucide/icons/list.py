
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def List(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list'], 'items': [{'path': {'d': 'M3 5h.01'}}, {'path': {'d': 'M3 12h.01'}}, {'path': {'d': 'M3 19h.01'}}, {'path': {'d': 'M8 5h13'}}, {'path': {'d': 'M8 12h13'}}, {'path': {'d': 'M8 19h13'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
