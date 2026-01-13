
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitCommitHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-commit-horizontal'], 'items': [{'circle': {'cx': '12', 'cy': '12', 'r': '3'}}, {'line': {'x1': '3', 'x2': '9', 'y1': '12', 'y2': '12'}}, {'line': {'x1': '15', 'x2': '21', 'y1': '12', 'y2': '12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
