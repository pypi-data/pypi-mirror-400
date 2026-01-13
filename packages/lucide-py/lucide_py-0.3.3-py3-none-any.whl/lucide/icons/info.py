
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Info(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-info'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '10'}}, {'path': {'d': 'M12 16v-4'}}, {'path': {'d': 'M12 8h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
