
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Skull(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-skull'], 'items': [{'path': {'d': 'm12.5 17-.5-1-.5 1h1z'}}, {'path': {'d': 'M15 22a1 1 0 0 0 1-1v-1a2 2 0 0 0 1.56-3.25 8 8 0 1 0-11.12 0A2 2 0 0 0 8 20v1a1 1 0 0 0 1 1z'}}, {'circle': {'cx': '15', 'cy': '12', 'r': '1'}}, {'circle': {'cx': '9', 'cy': '12', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
