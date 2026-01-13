
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Reply(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-reply'], 'items': [{'path': {'d': 'M20 18v-2a4 4 0 0 0-4-4H4'}}, {'path': {'d': 'm9 17-5-5 5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
