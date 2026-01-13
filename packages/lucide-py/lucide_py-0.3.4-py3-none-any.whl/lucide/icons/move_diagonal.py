
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MoveDiagonal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move-diagonal'], 'items': [{'path': {'d': 'M11 19H5v-6'}}, {'path': {'d': 'M13 5h6v6'}}, {'path': {'d': 'M19 5 5 19'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
