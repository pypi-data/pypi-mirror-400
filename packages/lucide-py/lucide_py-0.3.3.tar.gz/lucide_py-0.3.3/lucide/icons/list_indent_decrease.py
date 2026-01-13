
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListIndentDecrease(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-indent-decrease'], 'items': [{'path': {'d': 'M21 5H11'}}, {'path': {'d': 'M21 12H11'}}, {'path': {'d': 'M21 19H11'}}, {'path': {'d': 'm7 8-4 4 4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
