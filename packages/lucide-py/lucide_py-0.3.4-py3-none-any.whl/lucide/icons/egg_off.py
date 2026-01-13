
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def EggOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-egg-off'], 'items': [{'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M20 14.347V14c0-6-4-12-8-12-1.078 0-2.157.436-3.157 1.19'}}, {'path': {'d': 'M6.206 6.21C4.871 8.4 4 11.2 4 14a8 8 0 0 0 14.568 4.568'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
