
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowOutUpLeft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-out-up-left'], 'items': [{'path': {'d': 'M13 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-6'}}, {'path': {'d': 'm3 3 9 9'}}, {'path': {'d': 'M3 9V3h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
