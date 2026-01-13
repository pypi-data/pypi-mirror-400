
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Turntable(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-turntable'], 'items': [{'path': {'d': 'M10 12.01h.01'}}, {'path': {'d': 'M18 8v4a8 8 0 0 1-1.07 4'}}, {'circle': {'cx': '10', 'cy': '12', 'r': '4'}}, {'rect': {'x': '2', 'y': '4', 'width': '20', 'height': '16', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
