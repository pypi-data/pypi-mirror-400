
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Undo2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-undo-2'], 'items': [{'path': {'d': 'M9 14 4 9l5-5'}}, {'path': {'d': 'M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5a5.5 5.5 0 0 1-5.5 5.5H11'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
