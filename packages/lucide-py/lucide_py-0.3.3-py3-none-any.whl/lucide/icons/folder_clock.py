
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FolderClock(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-folder-clock'], 'items': [{'path': {'d': 'M16 14v2.2l1.6 1'}}, {'path': {'d': 'M7 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H20a2 2 0 0 1 2 2'}}, {'circle': {'cx': '16', 'cy': '16', 'r': '6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
