
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Merge(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-merge'], 'items': [{'path': {'d': 'm8 6 4-4 4 4'}}, {'path': {'d': 'M12 2v10.3a4 4 0 0 1-1.172 2.872L4 22'}}, {'path': {'d': 'm20 22-5-5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
