
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleDollarSign(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-dollar-sign'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8'}}, {'path': {'d': 'M12 18V6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
