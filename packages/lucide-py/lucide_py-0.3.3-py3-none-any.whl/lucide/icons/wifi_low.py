
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def WifiLow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-wifi-low'], 'items': [{'path': {'d': 'M12 20h.01'}}, {'path': {'d': 'M8.5 16.429a5 5 0 0 1 7 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
