
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LaptopMinimal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-laptop-minimal'], 'items': [{'rect': {'width': '18', 'height': '12', 'x': '3', 'y': '4', 'rx': '2', 'ry': '2'}}, {'line': {'x1': '2', 'x2': '22', 'y1': '20', 'y2': '20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
