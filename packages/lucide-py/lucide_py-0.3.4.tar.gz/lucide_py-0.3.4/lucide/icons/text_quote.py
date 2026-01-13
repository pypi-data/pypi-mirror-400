
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextQuote(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-quote'], 'items': [{'path': {'d': 'M17 5H3'}}, {'path': {'d': 'M21 12H8'}}, {'path': {'d': 'M21 19H8'}}, {'path': {'d': 'M3 12v7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
