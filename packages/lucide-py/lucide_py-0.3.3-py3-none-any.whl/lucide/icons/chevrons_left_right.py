
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsLeftRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-left-right'], 'items': [{'path': {'d': 'm9 7-5 5 5 5'}}, {'path': {'d': 'm15 7 5 5-5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
