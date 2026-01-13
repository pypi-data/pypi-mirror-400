
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelTopBottomDashed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panel-top-bottom-dashed'], 'items': [{'path': {'d': 'M14 15h1'}}, {'path': {'d': 'M14 9h1'}}, {'path': {'d': 'M19 15h2'}}, {'path': {'d': 'M19 9h2'}}, {'path': {'d': 'M3 15h2'}}, {'path': {'d': 'M3 9h2'}}, {'path': {'d': 'M9 15h1'}}, {'path': {'d': 'M9 9h1'}}, {'rect': {'x': '3', 'y': '3', 'width': '18', 'height': '18', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
