
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Eclipse(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-eclipse'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M12 2a7 7 0 1 0 10 10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
