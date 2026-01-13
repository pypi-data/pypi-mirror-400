
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def User(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user'], 'items': [{'path': {'d': 'M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2'}}, {'circle': {'cx': '12', 'cy': '7', 'r': '4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
