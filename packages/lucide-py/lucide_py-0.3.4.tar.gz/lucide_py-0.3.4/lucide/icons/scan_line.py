
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ScanLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-scan-line'], 'items': [{'path': {'d': 'M3 7V5a2 2 0 0 1 2-2h2'}}, {'path': {'d': 'M17 3h2a2 2 0 0 1 2 2v2'}}, {'path': {'d': 'M21 17v2a2 2 0 0 1-2 2h-2'}}, {'path': {'d': 'M7 21H5a2 2 0 0 1-2-2v-2'}}, {'path': {'d': 'M7 12h10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
