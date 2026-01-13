
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Sunrise(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-sunrise'], 'items': [{'path': {'d': 'M12 2v8'}}, {'path': {'d': 'm4.93 10.93 1.41 1.41'}}, {'path': {'d': 'M2 18h2'}}, {'path': {'d': 'M20 18h2'}}, {'path': {'d': 'm19.07 10.93-1.41 1.41'}}, {'path': {'d': 'M22 22H2'}}, {'path': {'d': 'm8 6 4-4 4 4'}}, {'path': {'d': 'M16 18a4 4 0 0 0-8 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
