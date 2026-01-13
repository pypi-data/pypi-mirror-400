
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-up'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'm16 12-4-4-4 4'}}, {'path': {'d': 'M12 16V8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
