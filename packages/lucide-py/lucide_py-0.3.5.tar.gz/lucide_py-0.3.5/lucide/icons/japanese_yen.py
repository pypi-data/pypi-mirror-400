
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def JapaneseYen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-japanese-yen'], 'items': [{'path': {'d': 'M12 9.5V21m0-11.5L6 3m6 6.5L18 3'}}, {'path': {'d': 'M6 15h12'}}, {'path': {'d': 'M6 11h12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
