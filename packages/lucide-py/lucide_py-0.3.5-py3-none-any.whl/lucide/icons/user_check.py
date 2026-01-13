
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-check'], 'items': [{'path': {'d': 'm16 11 2 2 4-4'}}, {'path': {'d': 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'}}, {'circle': {'cx': '9', 'cy': '7', 'r': '4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
