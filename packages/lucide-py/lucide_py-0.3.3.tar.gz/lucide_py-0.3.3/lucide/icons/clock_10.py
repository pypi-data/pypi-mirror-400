
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Clock10(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-10'], 'items': [{'path': {'d': 'M12 6v6l-4-2'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
