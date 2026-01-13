
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RotateCwSquare(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rotate-cw-square'], 'items': [{'path': {'d': 'M12 5H6a2 2 0 0 0-2 2v3'}}, {'path': {'d': 'm9 8 3-3-3-3'}}, {'path': {'d': 'M4 14v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
