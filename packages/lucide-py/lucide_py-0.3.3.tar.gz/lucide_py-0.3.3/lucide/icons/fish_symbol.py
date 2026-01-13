
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FishSymbol(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-fish-symbol'], 'items': [{'path': {'d': 'M2 16s9-15 20-4C11 23 2 8 2 8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
