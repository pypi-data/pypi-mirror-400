
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowLeftRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-left-right'], 'items': [{'path': {'d': 'M8 3 4 7l4 4'}}, {'path': {'d': 'M4 7h16'}}, {'path': {'d': 'm16 21 4-4-4-4'}}, {'path': {'d': 'M20 17H4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
