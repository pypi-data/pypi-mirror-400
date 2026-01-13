
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Vote(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-vote'], 'items': [{'path': {'d': 'm9 12 2 2 4-4'}}, {'path': {'d': 'M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7Z'}}, {'path': {'d': 'M22 19H2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
