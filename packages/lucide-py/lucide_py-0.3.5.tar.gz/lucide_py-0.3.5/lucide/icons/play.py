
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Play(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-play'], 'items': [{'path': {'d': 'M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
