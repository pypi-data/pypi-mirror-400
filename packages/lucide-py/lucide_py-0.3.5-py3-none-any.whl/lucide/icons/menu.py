
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Menu(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-menu'], 'items': [{'path': {'d': 'M4 5h16'}}, {'path': {'d': 'M4 12h16'}}, {'path': {'d': 'M4 19h16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
