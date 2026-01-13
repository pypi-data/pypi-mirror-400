
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-left'], 'items': [{'path': {'d': 'M6 8L2 12L6 16'}}, {'path': {'d': 'M2 12H22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
