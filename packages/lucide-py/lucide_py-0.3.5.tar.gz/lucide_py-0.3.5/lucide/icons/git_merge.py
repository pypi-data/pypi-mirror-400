
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitMerge(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-merge'], 'items': [{'circle': {'cx': '18', 'cy': '18', 'r': '3'}}, {'circle': {'cx': '6', 'cy': '6', 'r': '3'}}, {'path': {'d': 'M6 21V9a9 9 0 0 0 9 9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
