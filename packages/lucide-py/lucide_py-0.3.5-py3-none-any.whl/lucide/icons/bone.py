
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bone(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bone'], 'items': [{'path': {'d': 'M17 10c.7-.7 1.69 0 2.5 0a2.5 2.5 0 1 0 0-5 .5.5 0 0 1-.5-.5 2.5 2.5 0 1 0-5 0c0 .81.7 1.8 0 2.5l-7 7c-.7.7-1.69 0-2.5 0a2.5 2.5 0 0 0 0 5c.28 0 .5.22.5.5a2.5 2.5 0 1 0 5 0c0-.81-.7-1.8 0-2.5Z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
