
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-up'], 'items': [{'path': {'d': 'M8 6L12 2L16 6'}}, {'path': {'d': 'M12 2V22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
