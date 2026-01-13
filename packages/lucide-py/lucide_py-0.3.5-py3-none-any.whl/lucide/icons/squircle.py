
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Squircle(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-squircle'], 'items': [{'path': {'d': 'M12 3c7.2 0 9 1.8 9 9s-1.8 9-9 9-9-1.8-9-9 1.8-9 9-9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
