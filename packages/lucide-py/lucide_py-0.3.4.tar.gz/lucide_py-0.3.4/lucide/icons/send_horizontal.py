
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SendHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-send-horizontal'], 'items': [{'path': {'d': 'M3.714 3.048a.498.498 0 0 0-.683.627l2.843 7.627a2 2 0 0 1 0 1.396l-2.842 7.627a.498.498 0 0 0 .682.627l18-8.5a.5.5 0 0 0 0-.904z'}}, {'path': {'d': 'M6 12h16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
