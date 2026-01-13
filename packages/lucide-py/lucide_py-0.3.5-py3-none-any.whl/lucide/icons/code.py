
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Code(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-code'], 'items': [{'path': {'d': 'm16 18 6-6-6-6'}}, {'path': {'d': 'm8 6-6 6 6 6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
