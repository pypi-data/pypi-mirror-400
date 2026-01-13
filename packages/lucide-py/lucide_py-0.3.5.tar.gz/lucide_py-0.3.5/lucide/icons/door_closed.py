
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def DoorClosed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-door-closed'], 'items': [{'path': {'d': 'M10 12h.01'}}, {'path': {'d': 'M18 20V6a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v14'}}, {'path': {'d': 'M2 20h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
