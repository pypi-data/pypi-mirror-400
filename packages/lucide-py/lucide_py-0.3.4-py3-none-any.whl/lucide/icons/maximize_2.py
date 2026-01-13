
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Maximize2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-maximize-2'], 'items': [{'path': {'d': 'M15 3h6v6'}}, {'path': {'d': 'm21 3-7 7'}}, {'path': {'d': 'm3 21 7-7'}}, {'path': {'d': 'M9 21H3v-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
