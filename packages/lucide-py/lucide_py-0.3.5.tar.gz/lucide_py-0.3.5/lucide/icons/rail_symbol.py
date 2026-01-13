
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RailSymbol(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-rail-symbol'], 'items': [{'path': {'d': 'M5 15h14'}}, {'path': {'d': 'M5 9h14'}}, {'path': {'d': 'm14 20-5-5 6-6-5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
