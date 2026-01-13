
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Mail(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mail'], 'items': [{'path': {'d': 'm22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7'}}, {'rect': {'x': '2', 'y': '4', 'width': '20', 'height': '16', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
