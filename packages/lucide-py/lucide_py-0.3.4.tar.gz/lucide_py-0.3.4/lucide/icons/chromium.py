
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Chromium(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-chromium'], 'items': [{'path': {'d': 'M10.88 21.94 15.46 14'}}, {'path': {'d': 'M21.17 8H12'}}, {'path': {'d': 'M3.95 6.06 8.54 14'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
