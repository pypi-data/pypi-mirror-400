
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LampFloor(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-lamp-floor'], 'items': [{'path': {'d': 'M12 10v12'}}, {'path': {'d': 'M17.929 7.629A1 1 0 0 1 17 9H7a1 1 0 0 1-.928-1.371l2-5A1 1 0 0 1 9 2h6a1 1 0 0 1 .928.629z'}}, {'path': {'d': 'M9 22h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
