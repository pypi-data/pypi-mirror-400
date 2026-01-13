
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareEqual(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-equal'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M7 10h10'}}, {'path': {'d': 'M7 14h10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
