
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SignalHigh(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-signal-high'], 'items': [{'path': {'d': 'M2 20h.01'}}, {'path': {'d': 'M7 20v-4'}}, {'path': {'d': 'M12 20v-8'}}, {'path': {'d': 'M17 20V8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
