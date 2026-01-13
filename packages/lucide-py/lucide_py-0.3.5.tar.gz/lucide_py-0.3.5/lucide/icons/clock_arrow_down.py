
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ClockArrowDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-arrow-down'], 'items': [{'path': {'d': 'M12 6v6l2 1'}}, {'path': {'d': 'M12.337 21.994a10 10 0 1 1 9.588-8.767'}}, {'path': {'d': 'm14 18 4 4 4-4'}}, {'path': {'d': 'M18 14v8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
