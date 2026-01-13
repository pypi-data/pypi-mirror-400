
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelRightDashed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-right-dashed'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M15 14v1'}}, {'path': {'d': 'M15 19v2'}}, {'path': {'d': 'M15 3v2'}}, {'path': {'d': 'M15 9v1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
