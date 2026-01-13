
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FolderMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-folder-minus'], 'items': [{'path': {'d': 'M9 13h6'}}, {'path': {'d': 'M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
