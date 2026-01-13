
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FlipHorizontal2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-flip-horizontal-2'], 'items': [{'path': {'d': 'm3 7 5 5-5 5V7'}}, {'path': {'d': 'm21 7-5 5 5 5V7'}}, {'path': {'d': 'M12 20v2'}}, {'path': {'d': 'M12 14v2'}}, {'path': {'d': 'M12 8v2'}}, {'path': {'d': 'M12 2v2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
