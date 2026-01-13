
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlagTriangleRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flag-triangle-right'], 'items': [{'path': {'d': 'M6 22V2.8a.8.8 0 0 1 1.17-.71l11.38 5.69a.8.8 0 0 1 0 1.44L6 15.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
