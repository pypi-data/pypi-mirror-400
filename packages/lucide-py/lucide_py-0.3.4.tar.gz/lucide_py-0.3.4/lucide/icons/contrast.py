
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Contrast(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-contrast'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M12 18a6 6 0 0 0 0-12v12z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
