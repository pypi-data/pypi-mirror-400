
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FolderCode(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-folder-code'], 'items': [{'path': {'d': 'M10 10.5 8 13l2 2.5'}}, {'path': {'d': 'm14 10.5 2 2.5-2 2.5'}}, {'path': {'d': 'M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
