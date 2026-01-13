
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextAlignStart(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-align-start'], 'items': [{'path': {'d': 'M21 5H3'}}, {'path': {'d': 'M15 12H3'}}, {'path': {'d': 'M17 19H3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
