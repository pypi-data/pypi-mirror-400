
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitBranchMinus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-branch-minus'], 'items': [{'path': {'d': 'M15 6a9 9 0 0 0-9 9V3'}}, {'path': {'d': 'M21 18h-6'}}, {'circle': {'cx': '18', 'cy': '6', 'r': '3'}}, {'circle': {'cx': '6', 'cy': '18', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
