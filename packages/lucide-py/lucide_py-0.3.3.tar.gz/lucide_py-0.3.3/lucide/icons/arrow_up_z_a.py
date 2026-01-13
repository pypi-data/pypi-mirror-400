
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpZA(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-z-a'], 'items': [{'path': {'d': 'm3 8 4-4 4 4'}}, {'path': {'d': 'M7 4v16'}}, {'path': {'d': 'M15 4h5l-5 6h5'}}, {'path': {'d': 'M15 20v-3.5a2.5 2.5 0 0 1 5 0V20'}}, {'path': {'d': 'M20 18h-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
