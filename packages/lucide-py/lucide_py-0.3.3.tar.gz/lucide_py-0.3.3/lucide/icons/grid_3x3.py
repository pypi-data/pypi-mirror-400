
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Grid3x3(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-grid-3x3'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M3 9h18'}}, {'path': {'d': 'M3 15h18'}}, {'path': {'d': 'M9 3v18'}}, {'path': {'d': 'M15 3v18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
