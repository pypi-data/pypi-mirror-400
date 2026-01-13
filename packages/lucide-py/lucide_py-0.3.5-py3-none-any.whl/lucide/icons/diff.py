
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Diff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-diff'], 'items': [{'path': {'d': 'M12 3v14'}}, {'path': {'d': 'M5 10h14'}}, {'path': {'d': 'M5 21h14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
