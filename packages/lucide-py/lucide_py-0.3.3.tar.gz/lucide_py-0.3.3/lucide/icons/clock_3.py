
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Clock3(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-3'], 'items': [{'path': {'d': 'M12 6v6h4'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
