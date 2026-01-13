
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlipVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flip-vertical'], 'items': [{'path': {'d': 'M21 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v3'}}, {'path': {'d': 'M21 16v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3'}}, {'path': {'d': 'M4 12H2'}}, {'path': {'d': 'M10 12H8'}}, {'path': {'d': 'M16 12h-2'}}, {'path': {'d': 'M22 12h-2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
