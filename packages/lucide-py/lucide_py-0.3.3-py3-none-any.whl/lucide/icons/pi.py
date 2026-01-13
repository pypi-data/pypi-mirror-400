
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Pi(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pi'], 'items': [{'line': {'x1': '9', 'x2': '9', 'y1': '4', 'y2': '20'}}, {'path': {'d': 'M4 7c0-1.7 1.3-3 3-3h13'}}, {'path': {'d': 'M18 20c-1.7 0-3-1.3-3-3V4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
