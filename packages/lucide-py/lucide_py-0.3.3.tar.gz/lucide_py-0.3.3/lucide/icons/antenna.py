
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Antenna(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-antenna'], 'items': [{'path': {'d': 'M2 12 7 2'}}, {'path': {'d': 'm7 12 5-10'}}, {'path': {'d': 'm12 12 5-10'}}, {'path': {'d': 'm17 12 5-10'}}, {'path': {'d': 'M4.5 7h15'}}, {'path': {'d': 'M12 16v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
