
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ClockPlus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-plus'], 'items': [{'path': {'d': 'M12 6v6l3.644 1.822'}}, {'path': {'d': 'M16 19h6'}}, {'path': {'d': 'M19 16v6'}}, {'path': {'d': 'M21.92 13.267a10 10 0 1 0-8.653 8.653'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
