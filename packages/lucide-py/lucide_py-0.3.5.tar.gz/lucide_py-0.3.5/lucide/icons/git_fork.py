
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitFork(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-fork'], 'items': [{'circle': {'cx': '12', 'cy': '18', 'r': '3'}}, {'circle': {'cx': '6', 'cy': '6', 'r': '3'}}, {'circle': {'cx': '18', 'cy': '6', 'r': '3'}}, {'path': {'d': 'M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9'}}, {'path': {'d': 'M12 12v3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
