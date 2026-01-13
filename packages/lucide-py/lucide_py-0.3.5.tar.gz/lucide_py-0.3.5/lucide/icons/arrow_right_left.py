
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowRightLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-right-left'], 'items': [{'path': {'d': 'm16 3 4 4-4 4'}}, {'path': {'d': 'M20 7H4'}}, {'path': {'d': 'm8 21-4-4 4-4'}}, {'path': {'d': 'M4 17h16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
