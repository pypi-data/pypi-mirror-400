
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-right'], 'items': [{'path': {'d': 'm7 7 10 10'}}, {'path': {'d': 'M17 7v10H7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
