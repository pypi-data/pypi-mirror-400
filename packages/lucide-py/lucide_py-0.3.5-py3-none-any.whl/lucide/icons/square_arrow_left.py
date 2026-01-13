
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-left'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'm12 8-4 4 4 4'}}, {'path': {'d': 'M16 12H8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
