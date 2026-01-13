
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Mountain(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mountain'], 'items': [{'path': {'d': 'm8 3 4 8 5-5 5 15H2L8 3z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
