
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerDownRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-down-right'], 'items': [{'path': {'d': 'm15 10 5 5-5 5'}}, {'path': {'d': 'M4 4v7a4 4 0 0 0 4 4h12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
