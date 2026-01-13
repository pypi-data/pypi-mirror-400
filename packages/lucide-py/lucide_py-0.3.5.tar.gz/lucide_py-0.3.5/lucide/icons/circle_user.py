
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleUser(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-user'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'circle': {'cx': '12', 'cy': '10', 'r': '3'}}, {'path': {'d': 'M7 20.662V19a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v1.662'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
