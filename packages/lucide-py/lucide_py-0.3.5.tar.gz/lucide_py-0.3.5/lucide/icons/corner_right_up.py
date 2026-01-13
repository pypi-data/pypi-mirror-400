
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerRightUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-right-up'], 'items': [{'path': {'d': 'm10 9 5-5 5 5'}}, {'path': {'d': 'M4 20h7a4 4 0 0 0 4-4V4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
