
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Wifi(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-wifi'], 'items': [{'path': {'d': 'M12 20h.01'}}, {'path': {'d': 'M2 8.82a15 15 0 0 1 20 0'}}, {'path': {'d': 'M5 12.859a10 10 0 0 1 14 0'}}, {'path': {'d': 'M8.5 16.429a5 5 0 0 1 7 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
