
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitPullRequestDraft(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-pull-request-draft'], 'items': [{'circle': {'cx': '18', 'cy': '18', 'r': '3'}}, {'circle': {'cx': '6', 'cy': '6', 'r': '3'}}, {'path': {'d': 'M18 6V5'}}, {'path': {'d': 'M18 11v-1'}}, {'line': {'x1': '6', 'x2': '6', 'y1': '9', 'y2': '21'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
