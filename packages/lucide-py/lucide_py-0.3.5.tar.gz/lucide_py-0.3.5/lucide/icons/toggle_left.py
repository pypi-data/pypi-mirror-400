
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ToggleLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-toggle-left'], 'items': [{'circle': {'cx': '9', 'cy': '12', 'r': '3'}}, {'rect': {'width': '20', 'height': '14', 'x': '2', 'y': '5', 'rx': '7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
