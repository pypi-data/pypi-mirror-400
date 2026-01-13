
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FileKey(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-file-key'], 'items': [{'path': {'d': 'M10.65 22H18a2 2 0 0 0 2-2V8a2.4 2.4 0 0 0-.706-1.706l-3.588-3.588A2.4 2.4 0 0 0 14 2H6a2 2 0 0 0-2 2v10.1'}}, {'path': {'d': 'M14 2v5a1 1 0 0 0 1 1h5'}}, {'path': {'d': 'm10 15 1 1'}}, {'path': {'d': 'm11 14-4.586 4.586'}}, {'circle': {'cx': '5', 'cy': '20', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
