
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Library(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-library'], 'items': [{'path': {'d': 'm16 6 4 14'}}, {'path': {'d': 'M12 6v14'}}, {'path': {'d': 'M8 8v12'}}, {'path': {'d': 'M4 4v16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
