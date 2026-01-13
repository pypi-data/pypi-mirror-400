
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleCheckBig(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-check-big'], 'items': [{'path': {'d': 'M21.801 10A10 10 0 1 1 17 3.335'}}, {'path': {'d': 'm9 11 3 3L22 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
