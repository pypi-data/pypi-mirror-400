
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowOutDownLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-out-down-left'], 'items': [{'path': {'d': 'M2 12a10 10 0 1 1 10 10'}}, {'path': {'d': 'm2 22 10-10'}}, {'path': {'d': 'M8 22H2v-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
