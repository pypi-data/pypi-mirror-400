
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Headset(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-headset'], 'items': [{'path': {'d': 'M3 11h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-5Zm0 0a9 9 0 1 1 18 0m0 0v5a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3Z'}}, {'path': {'d': 'M21 16v2a4 4 0 0 1-4 4h-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
