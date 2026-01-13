
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Zap(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-zap'], 'items': [{'path': {'d': 'M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
