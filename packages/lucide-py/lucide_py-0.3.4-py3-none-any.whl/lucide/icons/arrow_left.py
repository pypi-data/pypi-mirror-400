
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-left'], 'items': [{'path': {'d': 'm12 19-7-7 7-7'}}, {'path': {'d': 'M19 12H5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
