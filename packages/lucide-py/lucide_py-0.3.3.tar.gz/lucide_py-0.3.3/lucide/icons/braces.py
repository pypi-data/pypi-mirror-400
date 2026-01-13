
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Braces(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-braces'], 'items': [{'path': {'d': 'M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5c0 1.1.9 2 2 2h1'}}, {'path': {'d': 'M16 21h1a2 2 0 0 0 2-2v-5c0-1.1.9-2 2-2a2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
