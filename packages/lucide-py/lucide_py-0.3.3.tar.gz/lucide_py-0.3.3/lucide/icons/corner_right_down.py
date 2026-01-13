
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerRightDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-right-down'], 'items': [{'path': {'d': 'm10 15 5 5 5-5'}}, {'path': {'d': 'M4 4h7a4 4 0 0 1 4 4v12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
