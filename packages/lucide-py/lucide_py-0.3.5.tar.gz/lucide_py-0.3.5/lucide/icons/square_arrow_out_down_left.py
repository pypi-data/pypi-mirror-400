
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowOutDownLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-out-down-left'], 'items': [{'path': {'d': 'M13 21h6a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v6'}}, {'path': {'d': 'm3 21 9-9'}}, {'path': {'d': 'M9 21H3v-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
