
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Shrink(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-shrink'], 'items': [{'path': {'d': 'm15 15 6 6m-6-6v4.8m0-4.8h4.8'}}, {'path': {'d': 'M9 19.8V15m0 0H4.2M9 15l-6 6'}}, {'path': {'d': 'M15 4.2V9m0 0h4.8M15 9l6-6'}}, {'path': {'d': 'M9 4.2V9m0 0H4.2M9 9 3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
