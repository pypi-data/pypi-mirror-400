
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownToLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-to-line'], 'items': [{'path': {'d': 'M12 17V3'}}, {'path': {'d': 'm6 11 6 6 6-6'}}, {'path': {'d': 'M19 21H5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
