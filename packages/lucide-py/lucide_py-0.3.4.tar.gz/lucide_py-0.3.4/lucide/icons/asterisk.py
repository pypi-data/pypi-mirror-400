
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Asterisk(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-asterisk'], 'items': [{'path': {'d': 'M12 6v12'}}, {'path': {'d': 'M17.196 9 6.804 15'}}, {'path': {'d': 'm6.804 9 10.392 6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
