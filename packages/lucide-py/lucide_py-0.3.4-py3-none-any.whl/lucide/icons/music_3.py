
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Music3(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-music-3'], 'items': [{'circle': {'cx': '12', 'cy': '18', 'r': '4'}}, {'path': {'d': 'M16 18V2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
