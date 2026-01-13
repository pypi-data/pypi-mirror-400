
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CloudOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cloud-off'], 'items': [{'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M5.782 5.782A7 7 0 0 0 9 19h8.5a4.5 4.5 0 0 0 1.307-.193'}}, {'path': {'d': 'M21.532 16.5A4.5 4.5 0 0 0 17.5 10h-1.79A7.008 7.008 0 0 0 10 5.07'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
