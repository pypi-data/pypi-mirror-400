
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveUpRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-up-right'], 'items': [{'path': {'d': 'M13 5H19V11'}}, {'path': {'d': 'M19 5L5 19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
