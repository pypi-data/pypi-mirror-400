
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowLeftFromLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-left-from-line'], 'items': [{'path': {'d': 'm9 6-6 6 6 6'}}, {'path': {'d': 'M3 12h14'}}, {'path': {'d': 'M21 19V5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
