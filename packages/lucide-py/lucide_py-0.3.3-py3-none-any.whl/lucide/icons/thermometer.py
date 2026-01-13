
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Thermometer(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-thermometer'], 'items': [{'path': {'d': 'M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
