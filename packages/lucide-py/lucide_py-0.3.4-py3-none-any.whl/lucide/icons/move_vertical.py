
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-vertical'], 'items': [{'path': {'d': 'M12 2v20'}}, {'path': {'d': 'm8 18 4 4 4-4'}}, {'path': {'d': 'm8 6 4-4 4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
