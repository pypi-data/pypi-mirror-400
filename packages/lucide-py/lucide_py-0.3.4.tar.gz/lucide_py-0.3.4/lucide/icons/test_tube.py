
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TestTube(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-test-tube'], 'items': [{'path': {'d': 'M14.5 2v17.5c0 1.4-1.1 2.5-2.5 2.5c-1.4 0-2.5-1.1-2.5-2.5V2'}}, {'path': {'d': 'M8.5 2h7'}}, {'path': {'d': 'M14.5 16h-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
