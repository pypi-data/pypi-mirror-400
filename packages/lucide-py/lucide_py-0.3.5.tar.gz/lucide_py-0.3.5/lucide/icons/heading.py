
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Heading(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-heading'], 'items': [{'path': {'d': 'M6 12h12'}}, {'path': {'d': 'M6 20V4'}}, {'path': {'d': 'M18 20V4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
