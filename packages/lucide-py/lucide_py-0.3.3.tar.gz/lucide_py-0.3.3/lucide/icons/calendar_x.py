
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CalendarX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-calendar-x'], 'items': [{'path': {'d': 'M8 2v4'}}, {'path': {'d': 'M16 2v4'}}, {'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M3 10h18'}}, {'path': {'d': 'm14 14-4 4'}}, {'path': {'d': 'm10 14 4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
