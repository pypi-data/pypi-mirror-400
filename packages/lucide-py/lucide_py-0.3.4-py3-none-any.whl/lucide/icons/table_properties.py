
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TableProperties(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-table-properties'], 'items': [{'path': {'d': 'M15 3v18'}}, {'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M21 9H3'}}, {'path': {'d': 'M21 15H3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
