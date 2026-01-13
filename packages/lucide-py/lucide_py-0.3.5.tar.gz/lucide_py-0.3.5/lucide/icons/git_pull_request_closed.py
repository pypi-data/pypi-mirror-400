
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def GitPullRequestClosed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-git-pull-request-closed'], 'items': [{'circle': {'cx': '6', 'cy': '6', 'r': '3'}}, {'path': {'d': 'M6 9v12'}}, {'path': {'d': 'm21 3-6 6'}}, {'path': {'d': 'm21 9-6-6'}}, {'path': {'d': 'M18 11.5V15'}}, {'circle': {'cx': '18', 'cy': '18', 'r': '3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
