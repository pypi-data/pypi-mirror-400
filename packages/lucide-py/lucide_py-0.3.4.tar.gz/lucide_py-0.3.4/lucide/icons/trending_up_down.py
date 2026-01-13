
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TrendingUpDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-trending-up-down'], 'items': [{'path': {'d': 'M14.828 14.828 21 21'}}, {'path': {'d': 'M21 16v5h-5'}}, {'path': {'d': 'm21 3-9 9-4-4-6 6'}}, {'path': {'d': 'M21 8V3h-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
