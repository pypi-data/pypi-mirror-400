
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GeorgianLari(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-georgian-lari'], 'items': [{'path': {'d': 'M11.5 21a7.5 7.5 0 1 1 7.35-9'}}, {'path': {'d': 'M13 12V3'}}, {'path': {'d': 'M4 21h16'}}, {'path': {'d': 'M9 12V3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
