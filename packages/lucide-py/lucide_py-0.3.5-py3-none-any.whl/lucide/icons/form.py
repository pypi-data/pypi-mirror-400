
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Form(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-form'], 'items': [{'path': {'d': 'M4 14h6'}}, {'path': {'d': 'M4 2h10'}}, {'rect': {'x': '4', 'y': '18', 'width': '16', 'height': '4', 'rx': '1'}}, {'rect': {'x': '4', 'y': '6', 'width': '16', 'height': '4', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
