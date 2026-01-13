
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Clock12(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-12'], 'items': [{'path': {'d': 'M12 6v6'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
