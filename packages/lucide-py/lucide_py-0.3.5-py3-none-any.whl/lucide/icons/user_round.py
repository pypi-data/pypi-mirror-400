
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserRound(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-round'], 'items': [{'circle': {'cx': '12', 'cy': '8', 'r': '5'}}, {'path': {'d': 'M20 21a8 8 0 0 0-16 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
