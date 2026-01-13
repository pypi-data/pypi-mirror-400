
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Globe(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-globe'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20'}}, {'path': {'d': 'M2 12h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
