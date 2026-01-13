
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AlignStartHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-align-start-horizontal'], 'items': [{'rect': {'width': '6', 'height': '16', 'x': '4', 'y': '6', 'rx': '2'}}, {'rect': {'width': '6', 'height': '9', 'x': '14', 'y': '6', 'rx': '2'}}, {'path': {'d': 'M22 2H2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
