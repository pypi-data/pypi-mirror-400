
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquarePlus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-plus'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M8 12h8'}}, {'path': {'d': 'M12 8v8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
