
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Copyright(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-copyright'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M14.83 14.83a4 4 0 1 1 0-5.66'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
