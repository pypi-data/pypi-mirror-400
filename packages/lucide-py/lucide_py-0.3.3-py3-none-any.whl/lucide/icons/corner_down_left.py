
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerDownLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-down-left'], 'items': [{'path': {'d': 'M20 4v7a4 4 0 0 1-4 4H4'}}, {'path': {'d': 'm9 10-5 5 5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
