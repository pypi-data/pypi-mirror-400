
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerUpLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-up-left'], 'items': [{'path': {'d': 'M20 20v-7a4 4 0 0 0-4-4H4'}}, {'path': {'d': 'M9 14 4 9l5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
