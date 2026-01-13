
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Check(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-check'], 'items': [{'path': {'d': 'M20 6 9 17l-5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
