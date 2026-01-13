
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Milestone(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-milestone'], 'items': [{'path': {'d': 'M12 13v8'}}, {'path': {'d': 'M12 3v3'}}, {'path': {'d': 'M4 6a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h13a2 2 0 0 0 1.152-.365l3.424-2.317a1 1 0 0 0 0-1.635l-3.424-2.318A2 2 0 0 0 17 6z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
