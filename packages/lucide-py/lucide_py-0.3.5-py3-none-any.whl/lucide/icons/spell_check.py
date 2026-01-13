
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SpellCheck(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-spell-check'], 'items': [{'path': {'d': 'm6 16 6-12 6 12'}}, {'path': {'d': 'M8 12h8'}}, {'path': {'d': 'm16 20 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
