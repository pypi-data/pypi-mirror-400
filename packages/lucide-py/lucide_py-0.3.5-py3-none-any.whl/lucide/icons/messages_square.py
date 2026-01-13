
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessagesSquare(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-messages-square'], 'items': [{'path': {'d': 'M16 10a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 14.286V4a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z'}}, {'path': {'d': 'M20 9a2 2 0 0 1 2 2v10.286a.71.71 0 0 1-1.212.502l-2.202-2.202A2 2 0 0 0 17.172 19H10a2 2 0 0 1-2-2v-1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
