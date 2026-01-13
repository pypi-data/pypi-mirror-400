
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MailOpen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-mail-open'], 'items': [{'path': {'d': 'M21.2 8.4c.5.38.8.97.8 1.6v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V10a2 2 0 0 1 .8-1.6l8-6a2 2 0 0 1 2.4 0l8 6Z'}}, {'path': {'d': 'm22 10-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 10'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
