
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Option(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-option'], 'items': [{'path': {'d': 'M3 3h6l6 18h6'}}, {'path': {'d': 'M14 3h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
