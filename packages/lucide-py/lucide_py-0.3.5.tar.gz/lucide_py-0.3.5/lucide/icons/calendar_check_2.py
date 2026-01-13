
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CalendarCheck2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-calendar-check-2'], 'items': [{'path': {'d': 'M8 2v4'}}, {'path': {'d': 'M16 2v4'}}, {'path': {'d': 'M21 14V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8'}}, {'path': {'d': 'M3 10h18'}}, {'path': {'d': 'm16 20 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
