
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CircleArrowOutUpRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-circle-arrow-out-up-right'], 'items': [{'path': {'d': 'M22 12A10 10 0 1 1 12 2'}}, {'path': {'d': 'M22 2 12 12'}}, {'path': {'d': 'M16 2h6v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
