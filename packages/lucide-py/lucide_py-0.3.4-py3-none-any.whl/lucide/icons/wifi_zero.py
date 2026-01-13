
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def WifiZero(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-wifi-zero'], 'items': [{'path': {'d': 'M12 20h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
