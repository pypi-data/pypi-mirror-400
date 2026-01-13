
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LocateOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-locate-off'], 'items': [{'path': {'d': 'M12 19v3'}}, {'path': {'d': 'M12 2v3'}}, {'path': {'d': 'M18.89 13.24a7 7 0 0 0-8.13-8.13'}}, {'path': {'d': 'M19 12h3'}}, {'path': {'d': 'M2 12h3'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M7.05 7.05a7 7 0 0 0 9.9 9.9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
