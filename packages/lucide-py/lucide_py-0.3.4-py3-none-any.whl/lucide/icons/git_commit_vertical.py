
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitCommitVertical(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-commit-vertical'], 'items': [{'path': {'d': 'M12 3v6'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '3'}}, {'path': {'d': 'M12 15v6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
