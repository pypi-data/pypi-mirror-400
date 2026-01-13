
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MarsStroke(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mars-stroke'], 'items': [{'path': {'d': 'm14 6 4 4'}}, {'path': {'d': 'M17 3h4v4'}}, {'path': {'d': 'm21 3-7.75 7.75'}}, {'circle': {'cx': '9', 'cy': '15', 'r': '6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
