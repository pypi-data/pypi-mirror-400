
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowRightFromLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-right-from-line'], 'items': [{'path': {'d': 'M3 5v14'}}, {'path': {'d': 'M21 12H7'}}, {'path': {'d': 'm15 18 6-6-6-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
