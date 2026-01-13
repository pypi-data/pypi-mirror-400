
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextAlignEnd(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-align-end'], 'items': [{'path': {'d': 'M21 5H3'}}, {'path': {'d': 'M21 12H9'}}, {'path': {'d': 'M21 19H7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
