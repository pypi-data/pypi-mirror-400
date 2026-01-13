
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-right'], 'items': [{'path': {'d': 'M18 8L22 12L18 16'}}, {'path': {'d': 'M2 12H22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
