
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Type(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-type'], 'items': [{'path': {'d': 'M12 4v16'}}, {'path': {'d': 'M4 7V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2'}}, {'path': {'d': 'M9 20h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
