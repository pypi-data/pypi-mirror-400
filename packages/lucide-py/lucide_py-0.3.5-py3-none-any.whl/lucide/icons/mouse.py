
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Mouse(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mouse'], 'items': [{'rect': {'x': '5', 'y': '2', 'width': '14', 'height': '20', 'rx': '7'}}, {'path': {'d': 'M12 6v4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
