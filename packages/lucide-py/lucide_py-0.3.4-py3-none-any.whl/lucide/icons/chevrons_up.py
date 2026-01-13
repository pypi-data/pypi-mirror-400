
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-up'], 'items': [{'path': {'d': 'm17 11-5-5-5 5'}}, {'path': {'d': 'm17 18-5-5-5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
