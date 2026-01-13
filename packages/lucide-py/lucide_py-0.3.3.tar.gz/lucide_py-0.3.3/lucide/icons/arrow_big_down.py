
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowBigDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-big-down'], 'items': [{'path': {'d': 'M15 11a1 1 0 0 0 1 1h2.939a1 1 0 0 1 .75 1.811l-6.835 6.836a1.207 1.207 0 0 1-1.707 0L4.31 13.81a1 1 0 0 1 .75-1.811H8a1 1 0 0 0 1-1V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
