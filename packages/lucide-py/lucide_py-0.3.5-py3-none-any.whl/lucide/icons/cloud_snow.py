
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CloudSnow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cloud-snow'], 'items': [{'path': {'d': 'M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242'}}, {'path': {'d': 'M8 15h.01'}}, {'path': {'d': 'M8 19h.01'}}, {'path': {'d': 'M12 17h.01'}}, {'path': {'d': 'M12 21h.01'}}, {'path': {'d': 'M16 15h.01'}}, {'path': {'d': 'M16 19h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
