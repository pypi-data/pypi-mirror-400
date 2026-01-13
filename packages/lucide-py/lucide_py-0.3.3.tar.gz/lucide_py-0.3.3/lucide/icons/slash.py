
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Slash(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-slash'], 'items': [{'path': {'d': 'M22 2 2 22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
