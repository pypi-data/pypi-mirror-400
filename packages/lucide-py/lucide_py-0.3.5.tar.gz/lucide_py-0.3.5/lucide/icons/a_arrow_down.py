
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def AArrowDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-a-arrow-down'], 'items': [{'path': {'d': 'm14 12 4 4 4-4'}}, {'path': {'d': 'M18 16V7'}}, {'path': {'d': 'm2 16 4.039-9.69a.5.5 0 0 1 .923 0L11 16'}}, {'path': {'d': 'M3.304 13h6.392'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
