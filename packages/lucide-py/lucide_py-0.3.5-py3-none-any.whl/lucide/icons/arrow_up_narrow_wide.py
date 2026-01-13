
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpNarrowWide(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-narrow-wide'], 'items': [{'path': {'d': 'm3 8 4-4 4 4'}}, {'path': {'d': 'M7 4v16'}}, {'path': {'d': 'M11 12h4'}}, {'path': {'d': 'M11 16h7'}}, {'path': {'d': 'M11 20h10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
