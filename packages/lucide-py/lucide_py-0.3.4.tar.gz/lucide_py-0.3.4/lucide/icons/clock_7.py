
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Clock7(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-7'], 'items': [{'path': {'d': 'M12 6v6l-2 4'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
