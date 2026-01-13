
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Pause(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pause'], 'items': [{'rect': {'x': '14', 'y': '3', 'width': '5', 'height': '18', 'rx': '1'}}, {'rect': {'x': '5', 'y': '3', 'width': '5', 'height': '18', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
