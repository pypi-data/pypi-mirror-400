
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowOutUpLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-out-up-left'], 'items': [{'path': {'d': 'M2 8V2h6'}}, {'path': {'d': 'm2 2 10 10'}}, {'path': {'d': 'M12 2A10 10 0 1 1 2 12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
