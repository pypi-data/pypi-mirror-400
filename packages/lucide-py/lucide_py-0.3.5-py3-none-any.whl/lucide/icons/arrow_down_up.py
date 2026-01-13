
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-up'], 'items': [{'path': {'d': 'm3 16 4 4 4-4'}}, {'path': {'d': 'M7 20V4'}}, {'path': {'d': 'm21 8-4-4-4 4'}}, {'path': {'d': 'M17 4v16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
