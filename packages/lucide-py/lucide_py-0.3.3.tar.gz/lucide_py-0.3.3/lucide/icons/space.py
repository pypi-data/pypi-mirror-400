
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Space(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-space'], 'items': [{'path': {'d': 'M22 17v1c0 .5-.5 1-1 1H3c-.5 0-1-.5-1-1v-1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
