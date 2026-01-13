
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Heading4(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-heading-4'], 'items': [{'path': {'d': 'M12 18V6'}}, {'path': {'d': 'M17 10v3a1 1 0 0 0 1 1h3'}}, {'path': {'d': 'M21 10v8'}}, {'path': {'d': 'M4 12h8'}}, {'path': {'d': 'M4 18V6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
