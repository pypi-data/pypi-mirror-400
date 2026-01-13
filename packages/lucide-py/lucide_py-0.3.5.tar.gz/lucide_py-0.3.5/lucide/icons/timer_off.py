
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TimerOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-timer-off'], 'items': [{'path': {'d': 'M10 2h4'}}, {'path': {'d': 'M4.6 11a8 8 0 0 0 1.7 8.7 8 8 0 0 0 8.7 1.7'}}, {'path': {'d': 'M7.4 7.4a8 8 0 0 1 10.3 1 8 8 0 0 1 .9 10.2'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M12 12v-2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
