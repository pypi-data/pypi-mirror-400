
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def StretchHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-stretch-horizontal'], 'items': [{'rect': {'width': '20', 'height': '6', 'x': '2', 'y': '4', 'rx': '2'}}, {'rect': {'width': '20', 'height': '6', 'x': '2', 'y': '14', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
