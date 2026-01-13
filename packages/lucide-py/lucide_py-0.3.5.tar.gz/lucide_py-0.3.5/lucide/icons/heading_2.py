
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Heading2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-heading-2'], 'items': [{'path': {'d': 'M4 12h8'}}, {'path': {'d': 'M4 18V6'}}, {'path': {'d': 'M12 18V6'}}, {'path': {'d': 'M21 18h-4c0-4 4-3 4-6 0-1.5-2-2.5-4-1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
