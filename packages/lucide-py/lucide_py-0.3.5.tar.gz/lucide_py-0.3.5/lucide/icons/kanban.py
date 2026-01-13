
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Kanban(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-kanban'], 'items': [{'path': {'d': 'M5 3v14'}}, {'path': {'d': 'M12 3v8'}}, {'path': {'d': 'M19 3v18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
