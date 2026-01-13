
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelRightClose(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-right-close'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M15 3v18'}}, {'path': {'d': 'm8 9 3 3-3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
