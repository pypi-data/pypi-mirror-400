
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowOutDownRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-out-down-right'], 'items': [{'path': {'d': 'M12 22a10 10 0 1 1 10-10'}}, {'path': {'d': 'M22 22 12 12'}}, {'path': {'d': 'M22 16v6h-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
