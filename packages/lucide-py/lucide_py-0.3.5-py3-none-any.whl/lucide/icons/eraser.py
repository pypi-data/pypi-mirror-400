
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Eraser(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-eraser'], 'items': [{'path': {'d': 'M21 21H8a2 2 0 0 1-1.42-.587l-3.994-3.999a2 2 0 0 1 0-2.828l10-10a2 2 0 0 1 2.829 0l5.999 6a2 2 0 0 1 0 2.828L12.834 21'}}, {'path': {'d': 'm5.082 11.09 8.828 8.828'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
