
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Expand(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-expand'], 'items': [{'path': {'d': 'm15 15 6 6'}}, {'path': {'d': 'm15 9 6-6'}}, {'path': {'d': 'M21 16v5h-5'}}, {'path': {'d': 'M21 8V3h-5'}}, {'path': {'d': 'M3 16v5h5'}}, {'path': {'d': 'm3 21 6-6'}}, {'path': {'d': 'M3 8V3h5'}}, {'path': {'d': 'M9 9 3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
