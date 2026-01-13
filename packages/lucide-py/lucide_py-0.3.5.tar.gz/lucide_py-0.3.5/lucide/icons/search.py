
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Search(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-search'], 'items': [{'path': {'d': 'm21 21-4.34-4.34'}}, {'circle': {'cx': '11', 'cy': '11', 'r': '8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
