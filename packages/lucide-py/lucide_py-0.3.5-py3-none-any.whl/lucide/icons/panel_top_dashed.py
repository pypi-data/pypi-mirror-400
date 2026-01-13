
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelTopDashed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-top-dashed'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M14 9h1'}}, {'path': {'d': 'M19 9h2'}}, {'path': {'d': 'M3 9h2'}}, {'path': {'d': 'M9 9h1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
