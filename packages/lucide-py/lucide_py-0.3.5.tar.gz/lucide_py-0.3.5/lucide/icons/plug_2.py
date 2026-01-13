
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Plug2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-plug-2'], 'items': [{'path': {'d': 'M9 2v6'}}, {'path': {'d': 'M15 2v6'}}, {'path': {'d': 'M12 17v5'}}, {'path': {'d': 'M5 8h14'}}, {'path': {'d': 'M6 11V8h12v3a6 6 0 1 1-12 0Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
