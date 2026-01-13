
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PilcrowRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-pilcrow-right'], 'items': [{'path': {'d': 'M10 3v11'}}, {'path': {'d': 'M10 9H7a1 1 0 0 1 0-6h8'}}, {'path': {'d': 'M14 3v11'}}, {'path': {'d': 'm18 14 4 4H2'}}, {'path': {'d': 'm22 18-4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
