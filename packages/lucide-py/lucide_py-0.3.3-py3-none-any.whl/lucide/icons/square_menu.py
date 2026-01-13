
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareMenu(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-menu'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M7 8h10'}}, {'path': {'d': 'M7 12h10'}}, {'path': {'d': 'M7 16h10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
