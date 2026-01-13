
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BookX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-book-x'], 'items': [{'path': {'d': 'm14.5 7-5 5'}}, {'path': {'d': 'M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20'}}, {'path': {'d': 'm9.5 7 5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
