
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Battery(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-battery'], 'items': [{'path': {'d': 'M 22 14 L 22 10'}}, {'rect': {'x': '2', 'y': '6', 'width': '16', 'height': '12', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
