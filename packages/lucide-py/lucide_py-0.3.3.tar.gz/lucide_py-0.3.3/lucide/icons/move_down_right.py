
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveDownRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-down-right'], 'items': [{'path': {'d': 'M19 13V19H13'}}, {'path': {'d': 'M5 5L19 19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
