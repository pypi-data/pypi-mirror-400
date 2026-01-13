
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-down'], 'items': [{'path': {'d': 'm21 16-4 4-4-4'}}, {'path': {'d': 'M17 20V4'}}, {'path': {'d': 'm3 8 4-4 4 4'}}, {'path': {'d': 'M7 4v16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
