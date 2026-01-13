
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignEndVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-end-vertical'], 'items': [{'rect': {'width': '16', 'height': '6', 'x': '2', 'y': '4', 'rx': '2'}}, {'rect': {'width': '9', 'height': '6', 'x': '9', 'y': '14', 'rx': '2'}}, {'path': {'d': 'M22 22V2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
