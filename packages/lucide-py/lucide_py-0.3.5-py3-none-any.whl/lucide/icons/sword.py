
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Sword(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-sword'], 'items': [{'path': {'d': 'm11 19-6-6'}}, {'path': {'d': 'm5 21-2-2'}}, {'path': {'d': 'm8 16-4 4'}}, {'path': {'d': 'M9.5 17.5 21 6V3h-3L6.5 14.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
