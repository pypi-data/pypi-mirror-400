
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TableOfContents(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-table-of-contents'], 'items': [{'path': {'d': 'M16 5H3'}}, {'path': {'d': 'M16 12H3'}}, {'path': {'d': 'M16 19H3'}}, {'path': {'d': 'M21 5h.01'}}, {'path': {'d': 'M21 12h.01'}}, {'path': {'d': 'M21 19h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
