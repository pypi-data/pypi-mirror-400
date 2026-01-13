
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownToDot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-to-dot'], 'items': [{'path': {'d': 'M12 2v14'}}, {'path': {'d': 'm19 9-7 7-7-7'}}, {'circle': {'cx': '12', 'cy': '21', 'r': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
