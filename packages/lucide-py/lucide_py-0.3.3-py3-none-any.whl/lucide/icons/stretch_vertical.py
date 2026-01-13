
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def StretchVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-stretch-vertical'], 'items': [{'rect': {'width': '6', 'height': '20', 'x': '4', 'y': '2', 'rx': '2'}}, {'rect': {'width': '6', 'height': '20', 'x': '14', 'y': '2', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
