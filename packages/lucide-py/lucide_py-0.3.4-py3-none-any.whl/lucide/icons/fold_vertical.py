
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FoldVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-fold-vertical'], 'items': [{'path': {'d': 'M12 22v-6'}}, {'path': {'d': 'M12 8V2'}}, {'path': {'d': 'M4 12H2'}}, {'path': {'d': 'M10 12H8'}}, {'path': {'d': 'M16 12h-2'}}, {'path': {'d': 'M22 12h-2'}}, {'path': {'d': 'm15 19-3-3-3 3'}}, {'path': {'d': 'm15 5-3 3-3-3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
