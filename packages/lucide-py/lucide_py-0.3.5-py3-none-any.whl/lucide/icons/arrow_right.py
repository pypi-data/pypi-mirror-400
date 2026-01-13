
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-right'], 'items': [{'path': {'d': 'M5 12h14'}}, {'path': {'d': 'm12 5 7 7-7 7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
