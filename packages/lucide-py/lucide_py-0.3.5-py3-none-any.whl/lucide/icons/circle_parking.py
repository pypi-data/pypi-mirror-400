
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleParking(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-parking'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M9 17V7h4a3 3 0 0 1 0 6H9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
