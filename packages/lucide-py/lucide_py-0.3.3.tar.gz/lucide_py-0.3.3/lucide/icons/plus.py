
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Plus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-plus'], 'items': [{'path': {'d': 'M5 12h14'}}, {'path': {'d': 'M12 5v14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
