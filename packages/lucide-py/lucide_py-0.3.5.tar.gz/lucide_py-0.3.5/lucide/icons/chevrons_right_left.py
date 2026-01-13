
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronsRightLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevrons-right-left'], 'items': [{'path': {'d': 'm20 17-5-5 5-5'}}, {'path': {'d': 'm4 17 5-5-5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
