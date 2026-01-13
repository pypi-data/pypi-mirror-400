
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelBottomDashed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-bottom-dashed'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M14 15h1'}}, {'path': {'d': 'M19 15h2'}}, {'path': {'d': 'M3 15h2'}}, {'path': {'d': 'M9 15h1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
