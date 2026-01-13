
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CalendarX2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-calendar-x-2'], 'items': [{'path': {'d': 'M8 2v4'}}, {'path': {'d': 'M16 2v4'}}, {'path': {'d': 'M21 13V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8'}}, {'path': {'d': 'M3 10h18'}}, {'path': {'d': 'm17 22 5-5'}}, {'path': {'d': 'm17 17 5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
