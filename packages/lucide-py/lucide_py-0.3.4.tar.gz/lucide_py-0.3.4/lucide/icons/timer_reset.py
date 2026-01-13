
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TimerReset(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-timer-reset'], 'items': [{'path': {'d': 'M10 2h4'}}, {'path': {'d': 'M12 14v-4'}}, {'path': {'d': 'M4 13a8 8 0 0 1 8-7 8 8 0 1 1-5.3 14L4 17.6'}}, {'path': {'d': 'M9 17H4v5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
