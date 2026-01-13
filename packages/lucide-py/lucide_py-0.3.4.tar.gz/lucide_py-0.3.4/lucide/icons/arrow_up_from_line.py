
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowUpFromLine(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-up-from-line'], 'items': [{'path': {'d': 'm18 9-6-6-6 6'}}, {'path': {'d': 'M12 3v14'}}, {'path': {'d': 'M5 21h14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
