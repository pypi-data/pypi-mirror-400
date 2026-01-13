
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveUpLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-up-left'], 'items': [{'path': {'d': 'M5 11V5H11'}}, {'path': {'d': 'M5 5L19 19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
