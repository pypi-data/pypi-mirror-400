
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bluetooth(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bluetooth'], 'items': [{'path': {'d': 'm7 7 10 10-5 5V2l5 5L7 17'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
