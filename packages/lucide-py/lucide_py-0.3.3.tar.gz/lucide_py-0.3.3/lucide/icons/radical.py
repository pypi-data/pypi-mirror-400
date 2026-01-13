
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Radical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-radical'], 'items': [{'path': {'d': 'M3 12h3.28a1 1 0 0 1 .948.684l2.298 7.934a.5.5 0 0 0 .96-.044L13.82 4.771A1 1 0 0 1 14.792 4H21'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
