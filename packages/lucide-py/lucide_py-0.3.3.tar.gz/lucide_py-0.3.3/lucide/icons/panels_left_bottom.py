
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PanelsLeftBottom(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-panels-left-bottom'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M9 3v18'}}, {'path': {'d': 'M9 15h12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
