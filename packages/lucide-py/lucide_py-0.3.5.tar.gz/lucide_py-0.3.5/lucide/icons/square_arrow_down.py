
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-down'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M12 8v8'}}, {'path': {'d': 'm8 12 4 4 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
