
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-left'], 'items': [{'path': {'d': 'M7 17V7h10'}}, {'path': {'d': 'M17 17 7 7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
