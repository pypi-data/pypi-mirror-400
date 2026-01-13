
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowLeftToLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-left-to-line'], 'items': [{'path': {'d': 'M3 19V5'}}, {'path': {'d': 'm13 6-6 6 6 6'}}, {'path': {'d': 'M7 12h14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
