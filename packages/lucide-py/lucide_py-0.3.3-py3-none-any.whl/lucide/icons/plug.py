
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Plug(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-plug'], 'items': [{'path': {'d': 'M12 22v-5'}}, {'path': {'d': 'M15 8V2'}}, {'path': {'d': 'M17 8a1 1 0 0 1 1 1v4a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1z'}}, {'path': {'d': 'M9 8V2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
