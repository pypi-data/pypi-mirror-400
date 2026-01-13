
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Framer(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-framer'], 'items': [{'path': {'d': 'M5 16V9h14V2H5l14 14h-7m-7 0 7 7v-7m-7 0h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
