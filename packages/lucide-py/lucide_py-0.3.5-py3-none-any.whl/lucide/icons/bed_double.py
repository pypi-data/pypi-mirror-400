
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BedDouble(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bed-double'], 'items': [{'path': {'d': 'M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8'}}, {'path': {'d': 'M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4'}}, {'path': {'d': 'M12 4v6'}}, {'path': {'d': 'M2 18h20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
