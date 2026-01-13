
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def IndianRupee(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-indian-rupee'], 'items': [{'path': {'d': 'M6 3h12'}}, {'path': {'d': 'M6 8h12'}}, {'path': {'d': 'm6 13 8.5 8'}}, {'path': {'d': 'M6 13h3'}}, {'path': {'d': 'M9 13c6.667 0 6.667-10 0-10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
