
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ClockArrowUp(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-clock-arrow-up'], 'items': [{'path': {'d': 'M12 6v6l1.56.78'}}, {'path': {'d': 'M13.227 21.925a10 10 0 1 1 8.767-9.588'}}, {'path': {'d': 'm14 18 4-4 4 4'}}, {'path': {'d': 'M18 22v-8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
