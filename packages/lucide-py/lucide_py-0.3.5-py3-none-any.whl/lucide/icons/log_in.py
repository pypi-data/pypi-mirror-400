
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LogIn(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-log-in'], 'items': [{'path': {'d': 'm10 17 5-5-5-5'}}, {'path': {'d': 'M15 12H3'}}, {'path': {'d': 'M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
