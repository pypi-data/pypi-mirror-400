
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RectangleEllipsis(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rectangle-ellipsis'], 'items': [{'rect': {'width': '20', 'height': '12', 'x': '2', 'y': '6', 'rx': '2'}}, {'path': {'d': 'M12 12h.01'}}, {'path': {'d': 'M17 12h.01'}}, {'path': {'d': 'M7 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
