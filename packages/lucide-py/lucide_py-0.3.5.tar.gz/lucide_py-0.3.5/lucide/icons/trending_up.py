
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TrendingUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-trending-up'], 'items': [{'path': {'d': 'M16 7h6v6'}}, {'path': {'d': 'm22 7-8.5 8.5-5-5L2 17'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
