
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LoaderCircle(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-loader-circle'], 'items': [{'path': {'d': 'M21 12a9 9 0 1 1-6.219-8.56'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
