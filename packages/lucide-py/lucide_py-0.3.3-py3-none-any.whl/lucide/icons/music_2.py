
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Music2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-music-2'], 'items': [{'circle': {'cx': '8', 'cy': '18', 'r': '4'}}, {'path': {'d': 'M12 18V2l7 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
