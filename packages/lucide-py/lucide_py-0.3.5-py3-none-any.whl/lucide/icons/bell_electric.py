
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BellElectric(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bell-electric'], 'items': [{'path': {'d': 'M18.518 17.347A7 7 0 0 1 14 19'}}, {'path': {'d': 'M18.8 4A11 11 0 0 1 20 9'}}, {'path': {'d': 'M9 9h.01'}}, {'circle': {'cx': '20', 'cy': '16', 'r': '2'}}, {'circle': {'cx': '9', 'cy': '9', 'r': '7'}}, {'rect': {'x': '4', 'y': '16', 'width': '10', 'height': '6', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
