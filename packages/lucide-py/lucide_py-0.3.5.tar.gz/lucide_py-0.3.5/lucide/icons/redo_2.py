
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Redo2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-redo-2'], 'items': [{'path': {'d': 'm15 14 5-5-5-5'}}, {'path': {'d': 'M20 9H9.5A5.5 5.5 0 0 0 4 14.5A5.5 5.5 0 0 0 9.5 20H13'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
