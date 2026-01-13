
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowsUpFromLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrows-up-from-line'], 'items': [{'path': {'d': 'm4 6 3-3 3 3'}}, {'path': {'d': 'M7 17V3'}}, {'path': {'d': 'm14 6 3-3 3 3'}}, {'path': {'d': 'M17 17V3'}}, {'path': {'d': 'M4 21h16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
