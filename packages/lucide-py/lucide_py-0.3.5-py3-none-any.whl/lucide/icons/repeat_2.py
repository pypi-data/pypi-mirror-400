
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Repeat2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-repeat-2'], 'items': [{'path': {'d': 'm2 9 3-3 3 3'}}, {'path': {'d': 'M13 18H7a2 2 0 0 1-2-2V6'}}, {'path': {'d': 'm22 15-3 3-3-3'}}, {'path': {'d': 'M11 6h6a2 2 0 0 1 2 2v10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
