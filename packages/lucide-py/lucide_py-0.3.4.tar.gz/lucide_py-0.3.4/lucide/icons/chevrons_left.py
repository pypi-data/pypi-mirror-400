
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-left'], 'items': [{'path': {'d': 'm11 17-5-5 5-5'}}, {'path': {'d': 'm18 17-5-5 5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
