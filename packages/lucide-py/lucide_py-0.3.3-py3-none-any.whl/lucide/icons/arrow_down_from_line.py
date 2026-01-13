
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownFromLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-from-line'], 'items': [{'path': {'d': 'M19 3H5'}}, {'path': {'d': 'M12 21V7'}}, {'path': {'d': 'm6 15 6 6 6-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
