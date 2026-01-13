
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareArrowOutDownRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-arrow-out-down-right'], 'items': [{'path': {'d': 'M21 11V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h6'}}, {'path': {'d': 'm21 21-9-9'}}, {'path': {'d': 'M21 15v6h-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
