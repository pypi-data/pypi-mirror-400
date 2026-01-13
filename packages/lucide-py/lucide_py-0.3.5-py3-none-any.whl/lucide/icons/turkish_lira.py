
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TurkishLira(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-turkish-lira'], 'items': [{'path': {'d': 'M15 4 5 9'}}, {'path': {'d': 'm15 8.5-10 5'}}, {'path': {'d': 'M18 12a9 9 0 0 1-9 9V3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
