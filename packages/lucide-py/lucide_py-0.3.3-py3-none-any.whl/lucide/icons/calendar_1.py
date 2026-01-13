
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Calendar1(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-calendar-1'], 'items': [{'path': {'d': 'M11 14h1v4'}}, {'path': {'d': 'M16 2v4'}}, {'path': {'d': 'M3 10h18'}}, {'path': {'d': 'M8 2v4'}}, {'rect': {'x': '3', 'y': '4', 'width': '18', 'height': '18', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
