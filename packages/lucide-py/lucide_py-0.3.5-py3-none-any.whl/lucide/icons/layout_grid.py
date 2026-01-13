
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LayoutGrid(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-layout-grid'], 'items': [{'rect': {'width': '7', 'height': '7', 'x': '3', 'y': '3', 'rx': '1'}}, {'rect': {'width': '7', 'height': '7', 'x': '14', 'y': '3', 'rx': '1'}}, {'rect': {'width': '7', 'height': '7', 'x': '14', 'y': '14', 'rx': '1'}}, {'rect': {'width': '7', 'height': '7', 'x': '3', 'y': '14', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
