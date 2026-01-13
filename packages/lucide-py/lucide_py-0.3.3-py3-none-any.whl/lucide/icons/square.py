
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Square(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
