
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CornerLeftDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-corner-left-down'], 'items': [{'path': {'d': 'm14 15-5 5-5-5'}}, {'path': {'d': 'M20 4h-7a4 4 0 0 0-4 4v12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
