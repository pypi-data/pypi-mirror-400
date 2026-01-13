
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-left'], 'items': [{'path': {'d': 'M17 7 7 17'}}, {'path': {'d': 'M17 17H7V7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
