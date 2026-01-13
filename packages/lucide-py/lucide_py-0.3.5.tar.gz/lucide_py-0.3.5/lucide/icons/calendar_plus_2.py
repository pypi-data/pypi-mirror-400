
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CalendarPlus2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-calendar-plus-2'], 'items': [{'path': {'d': 'M8 2v4'}}, {'path': {'d': 'M16 2v4'}}, {'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M3 10h18'}}, {'path': {'d': 'M10 16h4'}}, {'path': {'d': 'M12 14v4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
