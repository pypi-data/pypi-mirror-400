
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-right'], 'items': [{'path': {'d': 'm6 17 5-5-5-5'}}, {'path': {'d': 'm13 17 5-5-5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
