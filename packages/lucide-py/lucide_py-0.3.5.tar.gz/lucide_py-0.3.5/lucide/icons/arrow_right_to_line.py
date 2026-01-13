
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowRightToLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-right-to-line'], 'items': [{'path': {'d': 'M17 12H3'}}, {'path': {'d': 'm11 18 6-6-6-6'}}, {'path': {'d': 'M21 5v14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
