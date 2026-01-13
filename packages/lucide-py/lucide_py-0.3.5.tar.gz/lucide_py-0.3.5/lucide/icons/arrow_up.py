
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up'], 'items': [{'path': {'d': 'm5 12 7-7 7 7'}}, {'path': {'d': 'M12 19V5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
