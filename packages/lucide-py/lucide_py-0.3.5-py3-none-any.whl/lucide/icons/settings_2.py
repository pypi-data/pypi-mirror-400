
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Settings2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-settings-2'], 'items': [{'path': {'d': 'M14 17H5'}}, {'path': {'d': 'M19 7h-9'}}, {'circle': {'cx': '17', 'cy': '17', 'r': '3'}}, {'circle': {'cx': '7', 'cy': '7', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
