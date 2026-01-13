
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SpellCheck2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-spell-check-2'], 'items': [{'path': {'d': 'm6 16 6-12 6 12'}}, {'path': {'d': 'M8 12h8'}}, {'path': {'d': 'M4 21c1.1 0 1.1-1 2.3-1s1.1 1 2.3 1c1.1 0 1.1-1 2.3-1 1.1 0 1.1 1 2.3 1 1.1 0 1.1-1 2.3-1 1.1 0 1.1 1 2.3 1 1.1 0 1.1-1 2.3-1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
