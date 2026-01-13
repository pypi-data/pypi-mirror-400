
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelBottomOpen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-bottom-open'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M3 15h18'}}, {'path': {'d': 'm9 10 3-3 3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
