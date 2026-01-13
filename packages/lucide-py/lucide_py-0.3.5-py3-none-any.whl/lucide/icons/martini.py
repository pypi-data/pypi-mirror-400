
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Martini(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-martini'], 'items': [{'path': {'d': 'M8 22h8'}}, {'path': {'d': 'M12 11v11'}}, {'path': {'d': 'm19 3-7 8-7-8Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
