
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowOutUpRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-out-up-right'], 'items': [{'path': {'d': 'M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6'}}, {'path': {'d': 'm21 3-9 9'}}, {'path': {'d': 'M15 3h6v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
