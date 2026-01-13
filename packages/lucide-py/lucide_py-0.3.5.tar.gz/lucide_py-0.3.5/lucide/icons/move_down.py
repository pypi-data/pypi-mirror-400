
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-down'], 'items': [{'path': {'d': 'M8 18L12 22L16 18'}}, {'path': {'d': 'M12 2V22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
