
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LayoutList(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-layout-list'], 'items': [{'rect': {'width': '7', 'height': '7', 'x': '3', 'y': '3', 'rx': '1'}}, {'rect': {'width': '7', 'height': '7', 'x': '3', 'y': '14', 'rx': '1'}}, {'path': {'d': 'M14 4h7'}}, {'path': {'d': 'M14 9h7'}}, {'path': {'d': 'M14 15h7'}}, {'path': {'d': 'M14 20h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
