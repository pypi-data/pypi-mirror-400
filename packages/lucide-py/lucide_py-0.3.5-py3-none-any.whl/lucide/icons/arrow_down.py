
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down'], 'items': [{'path': {'d': 'M12 5v14'}}, {'path': {'d': 'm19 12-7 7-7-7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
