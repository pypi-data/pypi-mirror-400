
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Repeat(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-repeat'], 'items': [{'path': {'d': 'm17 2 4 4-4 4'}}, {'path': {'d': 'M3 11v-1a4 4 0 0 1 4-4h14'}}, {'path': {'d': 'm7 22-4-4 4-4'}}, {'path': {'d': 'M21 13v1a4 4 0 0 1-4 4H3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
