
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BetweenHorizontalStart(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-between-horizontal-start'], 'items': [{'rect': {'width': '13', 'height': '7', 'x': '8', 'y': '3', 'rx': '1'}}, {'path': {'d': 'm2 9 3 3-3 3'}}, {'rect': {'width': '13', 'height': '7', 'x': '8', 'y': '14', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
