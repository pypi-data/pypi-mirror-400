
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LayoutDashboard(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-layout-dashboard'], 'items': [{'rect': {'width': '7', 'height': '9', 'x': '3', 'y': '3', 'rx': '1'}}, {'rect': {'width': '7', 'height': '5', 'x': '14', 'y': '3', 'rx': '1'}}, {'rect': {'width': '7', 'height': '9', 'x': '14', 'y': '12', 'rx': '1'}}, {'rect': {'width': '7', 'height': '5', 'x': '3', 'y': '16', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
