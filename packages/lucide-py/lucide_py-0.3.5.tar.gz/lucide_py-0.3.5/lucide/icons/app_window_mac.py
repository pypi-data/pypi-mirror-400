
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AppWindowMac(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-app-window-mac'], 'items': [{'rect': {'width': '20', 'height': '16', 'x': '2', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M6 8h.01'}}, {'path': {'d': 'M10 8h.01'}}, {'path': {'d': 'M14 8h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
