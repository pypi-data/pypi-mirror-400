
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def UnfoldHorizontal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-unfold-horizontal'], 'items': [{'path': {'d': 'M16 12h6'}}, {'path': {'d': 'M8 12H2'}}, {'path': {'d': 'M12 2v2'}}, {'path': {'d': 'M12 8v2'}}, {'path': {'d': 'M12 14v2'}}, {'path': {'d': 'M12 20v2'}}, {'path': {'d': 'm19 15 3-3-3-3'}}, {'path': {'d': 'm5 9-3 3 3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
