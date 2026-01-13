
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SignalZero(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-signal-zero'], 'items': [{'path': {'d': 'M2 20h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
