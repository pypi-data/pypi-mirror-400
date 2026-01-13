
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def RemoveFormatting(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-remove-formatting'], 'items': [{'path': {'d': 'M4 7V4h16v3'}}, {'path': {'d': 'M5 20h6'}}, {'path': {'d': 'M13 4 8 20'}}, {'path': {'d': 'm15 15 5 5'}}, {'path': {'d': 'm20 15-5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
