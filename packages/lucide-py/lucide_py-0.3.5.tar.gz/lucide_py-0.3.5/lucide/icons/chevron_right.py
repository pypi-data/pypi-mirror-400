
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevron-right'], 'items': [{'path': {'d': 'm9 18 6-6-6-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
