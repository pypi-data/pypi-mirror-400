
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CloudAlert(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cloud-alert'], 'items': [{'path': {'d': 'M12 12v4'}}, {'path': {'d': 'M12 20h.01'}}, {'path': {'d': 'M17 18h.5a1 1 0 0 0 0-9h-1.79A7 7 0 1 0 7 17.708'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
