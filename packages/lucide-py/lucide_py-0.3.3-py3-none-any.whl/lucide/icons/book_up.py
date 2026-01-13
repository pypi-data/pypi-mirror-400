
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BookUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-book-up'], 'items': [{'path': {'d': 'M12 13V7'}}, {'path': {'d': 'M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20'}}, {'path': {'d': 'm9 10 3-3 3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
