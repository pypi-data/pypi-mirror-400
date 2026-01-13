
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TrendingDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-trending-down'], 'items': [{'path': {'d': 'M16 17h6v-6'}}, {'path': {'d': 'm22 17-8.5-8.5-5 5L2 7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
