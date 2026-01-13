
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BookmarkX(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bookmark-x'], 'items': [{'path': {'d': 'm19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2Z'}}, {'path': {'d': 'm14.5 7.5-5 5'}}, {'path': {'d': 'm9.5 7.5 5 5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
