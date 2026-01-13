
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Share(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-share'], 'items': [{'path': {'d': 'M12 2v13'}}, {'path': {'d': 'm16 6-4-4-4 4'}}, {'path': {'d': 'M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
