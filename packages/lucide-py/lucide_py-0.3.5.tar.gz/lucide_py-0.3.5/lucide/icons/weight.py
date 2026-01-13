
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Weight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-weight'], 'items': [{'circle': {'cx': '12', 'cy': '5', 'r': '3'}}, {'path': {'d': 'M6.5 8a2 2 0 0 0-1.905 1.46L2.1 18.5A2 2 0 0 0 4 21h16a2 2 0 0 0 1.925-2.54L19.4 9.5A2 2 0 0 0 17.48 8Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
