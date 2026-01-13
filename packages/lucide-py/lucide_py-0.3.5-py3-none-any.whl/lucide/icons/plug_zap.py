
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PlugZap(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-plug-zap'], 'items': [{'path': {'d': 'M6.3 20.3a2.4 2.4 0 0 0 3.4 0L12 18l-6-6-2.3 2.3a2.4 2.4 0 0 0 0 3.4Z'}}, {'path': {'d': 'm2 22 3-3'}}, {'path': {'d': 'M7.5 13.5 10 11'}}, {'path': {'d': 'M10.5 16.5 13 14'}}, {'path': {'d': 'm18 3-4 4h6l-4 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
