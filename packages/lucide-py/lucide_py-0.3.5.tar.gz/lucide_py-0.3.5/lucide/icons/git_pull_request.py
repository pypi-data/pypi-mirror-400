
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitPullRequest(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-pull-request'], 'items': [{'circle': {'cx': '18', 'cy': '18', 'r': '3'}}, {'circle': {'cx': '6', 'cy': '6', 'r': '3'}}, {'path': {'d': 'M13 6h3a2 2 0 0 1 2 2v7'}}, {'line': {'x1': '6', 'x2': '6', 'y1': '9', 'y2': '21'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
