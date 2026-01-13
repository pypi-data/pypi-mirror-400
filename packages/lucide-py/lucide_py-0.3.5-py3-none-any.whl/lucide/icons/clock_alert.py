
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ClockAlert(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-alert'], 'items': [{'path': {'d': 'M12 6v6l4 2'}}, {'path': {'d': 'M20 12v5'}}, {'path': {'d': 'M20 21h.01'}}, {'path': {'d': 'M21.25 8.2A10 10 0 1 0 16 21.16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
