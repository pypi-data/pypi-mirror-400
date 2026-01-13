
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ClockCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-check'], 'items': [{'path': {'d': 'M12 6v6l4 2'}}, {'path': {'d': 'M22 12a10 10 0 1 0-11 9.95'}}, {'path': {'d': 'm22 16-5.5 5.5L14 19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
