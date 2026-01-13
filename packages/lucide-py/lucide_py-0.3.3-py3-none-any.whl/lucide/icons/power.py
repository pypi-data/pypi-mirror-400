
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Power(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-power'], 'items': [{'path': {'d': 'M12 2v10'}}, {'path': {'d': 'M18.4 6.6a9 9 0 1 1-12.77.04'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
