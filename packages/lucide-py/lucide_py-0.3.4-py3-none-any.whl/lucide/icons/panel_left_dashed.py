
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelLeftDashed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-left-dashed'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M9 14v1'}}, {'path': {'d': 'M9 19v2'}}, {'path': {'d': 'M9 3v2'}}, {'path': {'d': 'M9 9v1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
