
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareParking(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-parking'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M9 17V7h4a3 3 0 0 1 0 6H9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
