
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BadgeTurkishLira(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-badge-turkish-lira'], 'items': [{'path': {'d': 'M11 7v10a5 5 0 0 0 5-5'}}, {'path': {'d': 'm15 8-6 3'}}, {'path': {'d': 'M3.85 8.62a4 4 0 0 1 4.78-4.77 4 4 0 0 1 6.74 0 4 4 0 0 1 4.78 4.78 4 4 0 0 1 0 6.74 4 4 0 0 1-4.77 4.78 4 4 0 0 1-6.75 0 4 4 0 0 1-4.78-4.77 4 4 0 0 1 0-6.76'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
