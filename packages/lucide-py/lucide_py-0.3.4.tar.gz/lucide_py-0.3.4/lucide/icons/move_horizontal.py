
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-horizontal'], 'items': [{'path': {'d': 'm18 8 4 4-4 4'}}, {'path': {'d': 'M2 12h20'}}, {'path': {'d': 'm6 8-4 4 4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
