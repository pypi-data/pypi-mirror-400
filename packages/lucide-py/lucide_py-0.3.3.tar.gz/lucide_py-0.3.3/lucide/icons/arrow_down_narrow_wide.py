
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownNarrowWide(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-narrow-wide'], 'items': [{'path': {'d': 'm3 16 4 4 4-4'}}, {'path': {'d': 'M7 20V4'}}, {'path': {'d': 'M11 4h4'}}, {'path': {'d': 'M11 8h7'}}, {'path': {'d': 'M11 12h10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
