
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Clock9(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-9'], 'items': [{'path': {'d': 'M12 6v6H8'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
