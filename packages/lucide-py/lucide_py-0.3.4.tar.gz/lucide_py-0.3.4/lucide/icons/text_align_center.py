
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextAlignCenter(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-align-center'], 'items': [{'path': {'d': 'M21 5H3'}}, {'path': {'d': 'M17 12H7'}}, {'path': {'d': 'M19 19H5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
