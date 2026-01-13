
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BetweenVerticalStart(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-between-vertical-start'], 'items': [{'rect': {'width': '7', 'height': '13', 'x': '3', 'y': '8', 'rx': '1'}}, {'path': {'d': 'm15 2-3 3-3-3'}}, {'rect': {'width': '7', 'height': '13', 'x': '14', 'y': '8', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
