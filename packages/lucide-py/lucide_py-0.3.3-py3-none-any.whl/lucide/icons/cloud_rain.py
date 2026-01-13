
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CloudRain(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cloud-rain'], 'items': [{'path': {'d': 'M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242'}}, {'path': {'d': 'M16 14v6'}}, {'path': {'d': 'M8 14v6'}}, {'path': {'d': 'M12 16v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
