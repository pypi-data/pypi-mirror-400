
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CodeXml(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-code-xml'], 'items': [{'path': {'d': 'm18 16 4-4-4-4'}}, {'path': {'d': 'm6 8-4 4 4 4'}}, {'path': {'d': 'm14.5 4-5 16'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
