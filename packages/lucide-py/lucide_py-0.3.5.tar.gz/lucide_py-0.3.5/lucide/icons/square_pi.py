
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquarePi(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-pi'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M7 7h10'}}, {'path': {'d': 'M10 7v10'}}, {'path': {'d': 'M16 17a2 2 0 0 1-2-2V7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
