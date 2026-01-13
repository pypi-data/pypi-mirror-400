
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def MessageSquareDashed(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-message-square-dashed'], 'items': [{'path': {'d': 'M12 19h.01'}}, {'path': {'d': 'M12 3h.01'}}, {'path': {'d': 'M16 19h.01'}}, {'path': {'d': 'M16 3h.01'}}, {'path': {'d': 'M2 13h.01'}}, {'path': {'d': 'M2 17v4.286a.71.71 0 0 0 1.212.502l2.202-2.202A2 2 0 0 1 6.828 19H8'}}, {'path': {'d': 'M2 5a2 2 0 0 1 2-2'}}, {'path': {'d': 'M2 9h.01'}}, {'path': {'d': 'M20 3a2 2 0 0 1 2 2'}}, {'path': {'d': 'M22 13h.01'}}, {'path': {'d': 'M22 17a2 2 0 0 1-2 2'}}, {'path': {'d': 'M22 9h.01'}}, {'path': {'d': 'M8 3h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
