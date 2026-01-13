
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ClosedCaption(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-closed-caption'], 'items': [{'path': {'d': 'M10 9.17a3 3 0 1 0 0 5.66'}}, {'path': {'d': 'M17 9.17a3 3 0 1 0 0 5.66'}}, {'rect': {'x': '2', 'y': '5', 'width': '20', 'height': '14', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
