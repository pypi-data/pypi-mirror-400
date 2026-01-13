
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ReplyAll(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-reply-all'], 'items': [{'path': {'d': 'm12 17-5-5 5-5'}}, {'path': {'d': 'M22 18v-2a4 4 0 0 0-4-4H7'}}, {'path': {'d': 'm7 17-5-5 5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
