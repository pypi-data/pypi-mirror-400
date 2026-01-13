
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LayoutTemplate(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-layout-template'], 'items': [{'rect': {'width': '18', 'height': '7', 'x': '3', 'y': '3', 'rx': '1'}}, {'rect': {'width': '9', 'height': '7', 'x': '3', 'y': '14', 'rx': '1'}}, {'rect': {'width': '5', 'height': '7', 'x': '16', 'y': '14', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
