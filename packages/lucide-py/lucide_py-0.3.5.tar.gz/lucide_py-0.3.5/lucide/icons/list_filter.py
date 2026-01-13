
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListFilter(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-filter'], 'items': [{'path': {'d': 'M2 5h20'}}, {'path': {'d': 'M6 12h12'}}, {'path': {'d': 'M9 19h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
