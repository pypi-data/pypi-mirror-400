
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-off'], 'items': [{'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M8.35 2.69A10 10 0 0 1 21.3 15.65'}}, {'path': {'d': 'M19.08 19.08A10 10 0 1 1 4.92 4.92'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
