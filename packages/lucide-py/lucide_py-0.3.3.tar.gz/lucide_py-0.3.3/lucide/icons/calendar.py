
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Calendar(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-calendar'], 'items': [{'path': {'d': 'M8 2v4'}}, {'path': {'d': 'M16 2v4'}}, {'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M3 10h18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
