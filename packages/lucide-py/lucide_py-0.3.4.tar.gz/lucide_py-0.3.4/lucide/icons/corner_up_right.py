
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerUpRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-up-right'], 'items': [{'path': {'d': 'm15 14 5-5-5-5'}}, {'path': {'d': 'M4 20v-7a4 4 0 0 1 4-4h12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
