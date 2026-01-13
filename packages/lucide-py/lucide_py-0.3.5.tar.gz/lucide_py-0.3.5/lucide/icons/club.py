
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Club(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-club'], 'items': [{'path': {'d': 'M17.28 9.05a5.5 5.5 0 1 0-10.56 0A5.5 5.5 0 1 0 12 17.66a5.5 5.5 0 1 0 5.28-8.6Z'}}, {'path': {'d': 'M12 17.66L12 22'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
