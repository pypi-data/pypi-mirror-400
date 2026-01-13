
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PersonStanding(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-person-standing'], 'items': [{'circle': {'cx': '12', 'cy': '5', 'r': '1'}}, {'path': {'d': 'm9 20 3-6 3 6'}}, {'path': {'d': 'm6 8 6 2 6-2'}}, {'path': {'d': 'M12 10v4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
