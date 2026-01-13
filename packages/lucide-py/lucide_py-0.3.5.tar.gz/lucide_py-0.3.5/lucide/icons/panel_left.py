
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-left'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M9 3v18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
