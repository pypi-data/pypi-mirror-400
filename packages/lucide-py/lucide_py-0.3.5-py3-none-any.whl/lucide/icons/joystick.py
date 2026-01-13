
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Joystick(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-joystick'], 'items': [{'path': {'d': 'M21 17a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-2Z'}}, {'path': {'d': 'M6 15v-2'}}, {'path': {'d': 'M12 15V9'}}, {'circle': {'cx': '12', 'cy': '6', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
