
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PilcrowLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pilcrow-left'], 'items': [{'path': {'d': 'M14 3v11'}}, {'path': {'d': 'M14 9h-3a3 3 0 0 1 0-6h9'}}, {'path': {'d': 'M18 3v11'}}, {'path': {'d': 'M22 18H2l4-4'}}, {'path': {'d': 'm6 22-4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
