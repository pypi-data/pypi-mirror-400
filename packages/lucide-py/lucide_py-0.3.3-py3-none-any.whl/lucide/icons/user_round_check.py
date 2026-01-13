
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UserRoundCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-user-round-check'], 'items': [{'path': {'d': 'M2 21a8 8 0 0 1 13.292-6'}}, {'circle': {'cx': '10', 'cy': '8', 'r': '5'}}, {'path': {'d': 'm16 19 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
