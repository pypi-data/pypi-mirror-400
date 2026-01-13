
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Wind(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-wind'], 'items': [{'path': {'d': 'M12.8 19.6A2 2 0 1 0 14 16H2'}}, {'path': {'d': 'M17.5 8a2.5 2.5 0 1 1 2 4H2'}}, {'path': {'d': 'M9.8 4.4A2 2 0 1 1 11 8H2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
