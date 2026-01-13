
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BedSingle(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bed-single'], 'items': [{'path': {'d': 'M3 20v-8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v8'}}, {'path': {'d': 'M5 10V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v4'}}, {'path': {'d': 'M3 18h18'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
