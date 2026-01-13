
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ChevronFirst(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chevron-first'], 'items': [{'path': {'d': 'm17 18-6-6 6-6'}}, {'path': {'d': 'M7 6v12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
