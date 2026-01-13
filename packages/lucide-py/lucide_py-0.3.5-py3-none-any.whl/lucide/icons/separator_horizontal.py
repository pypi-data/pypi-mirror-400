
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SeparatorHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-separator-horizontal'], 'items': [{'path': {'d': 'm16 16-4 4-4-4'}}, {'path': {'d': 'M3 12h18'}}, {'path': {'d': 'm8 8 4-4 4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
