
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Columns2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-columns-2'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M12 3v18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
