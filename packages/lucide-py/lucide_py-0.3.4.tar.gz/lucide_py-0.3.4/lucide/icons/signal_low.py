
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SignalLow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-signal-low'], 'items': [{'path': {'d': 'M2 20h.01'}}, {'path': {'d': 'M7 20v-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
