
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SeparatorVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-separator-vertical'], 'items': [{'path': {'d': 'M12 3v18'}}, {'path': {'d': 'm16 16 4-4-4-4'}}, {'path': {'d': 'm8 8-4 4 4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
