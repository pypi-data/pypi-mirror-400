
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Heading1(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-heading-1'], 'items': [{'path': {'d': 'M4 12h8'}}, {'path': {'d': 'M4 18V6'}}, {'path': {'d': 'M12 18V6'}}, {'path': {'d': 'm17 12 3-2v8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
