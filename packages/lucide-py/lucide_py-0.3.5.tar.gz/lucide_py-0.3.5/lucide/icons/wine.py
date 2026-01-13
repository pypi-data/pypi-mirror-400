
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Wine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-wine'], 'items': [{'path': {'d': 'M8 22h8'}}, {'path': {'d': 'M7 10h10'}}, {'path': {'d': 'M12 15v7'}}, {'path': {'d': 'M12 15a5 5 0 0 0 5-5c0-2-.5-4-2-8H9c-1.5 4-2 6-2 8a5 5 0 0 0 5 5Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
