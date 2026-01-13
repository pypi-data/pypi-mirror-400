
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CloudCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cloud-check'], 'items': [{'path': {'d': 'm17 15-5.5 5.5L9 18'}}, {'path': {'d': 'M5 17.743A7 7 0 1 1 15.71 10h1.79a4.5 4.5 0 0 1 1.5 8.742'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
