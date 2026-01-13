
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelTopOpen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-top-open'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M3 9h18'}}, {'path': {'d': 'm15 14-3 3-3-3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
