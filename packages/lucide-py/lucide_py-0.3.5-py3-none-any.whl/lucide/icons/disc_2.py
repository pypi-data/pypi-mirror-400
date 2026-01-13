
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Disc2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-disc-2'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '4'}}, {'path': {'d': 'M12 12h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
