
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Gauge(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-gauge'], 'items': [{'path': {'d': 'm12 14 4-4'}}, {'path': {'d': 'M3.34 19a10 10 0 1 1 17.32 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
