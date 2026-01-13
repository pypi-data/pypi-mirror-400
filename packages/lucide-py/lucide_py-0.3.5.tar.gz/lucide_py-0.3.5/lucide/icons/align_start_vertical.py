
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignStartVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-start-vertical'], 'items': [{'rect': {'width': '9', 'height': '6', 'x': '6', 'y': '14', 'rx': '2'}}, {'rect': {'width': '16', 'height': '6', 'x': '6', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M2 2v20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
