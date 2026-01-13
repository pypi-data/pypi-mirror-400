
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Move(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-move'], 'items': [{'path': {'d': 'M12 2v20'}}, {'path': {'d': 'm15 19-3 3-3-3'}}, {'path': {'d': 'm19 9 3 3-3 3'}}, {'path': {'d': 'M2 12h20'}}, {'path': {'d': 'm5 9-3 3 3 3'}}, {'path': {'d': 'm9 5 3-3 3 3'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
