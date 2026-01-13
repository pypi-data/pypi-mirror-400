
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Table2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-table-2'], 'items': [{'path': {'d': 'M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
