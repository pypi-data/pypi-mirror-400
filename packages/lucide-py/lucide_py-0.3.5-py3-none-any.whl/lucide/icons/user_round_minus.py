
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserRoundMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-round-minus'], 'items': [{'path': {'d': 'M2 21a8 8 0 0 1 13.292-6'}}, {'circle': {'cx': '10', 'cy': '8', 'r': '5'}}, {'path': {'d': 'M22 19h-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
