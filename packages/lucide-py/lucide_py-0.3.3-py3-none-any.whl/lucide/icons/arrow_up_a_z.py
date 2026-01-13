
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpAZ(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-a-z'], 'items': [{'path': {'d': 'm3 8 4-4 4 4'}}, {'path': {'d': 'M7 4v16'}}, {'path': {'d': 'M20 8h-5'}}, {'path': {'d': 'M15 10V6.5a2.5 2.5 0 0 1 5 0V10'}}, {'path': {'d': 'M15 14h5l-5 6h5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
