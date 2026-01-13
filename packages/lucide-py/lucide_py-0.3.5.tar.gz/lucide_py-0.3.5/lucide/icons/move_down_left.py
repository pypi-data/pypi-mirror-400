
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveDownLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-down-left'], 'items': [{'path': {'d': 'M11 19H5V13'}}, {'path': {'d': 'M19 5L5 19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
