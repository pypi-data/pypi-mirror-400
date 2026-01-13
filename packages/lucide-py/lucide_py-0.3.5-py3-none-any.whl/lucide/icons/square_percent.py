
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquarePercent(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-percent'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'm15 9-6 6'}}, {'path': {'d': 'M9 9h.01'}}, {'path': {'d': 'M15 15h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
