
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelLeftOpen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-left-open'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M9 3v18'}}, {'path': {'d': 'm14 9 3 3-3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
