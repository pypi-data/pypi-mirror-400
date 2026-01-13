
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-right'], 'items': [{'path': {'d': 'M7 7h10v10'}}, {'path': {'d': 'M7 17 17 7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
