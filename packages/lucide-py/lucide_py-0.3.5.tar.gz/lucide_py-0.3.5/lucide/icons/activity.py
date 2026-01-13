
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Activity(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-activity'], 'items': [{'path': {'d': 'M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
