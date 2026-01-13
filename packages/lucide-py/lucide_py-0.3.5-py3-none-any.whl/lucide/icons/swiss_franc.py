
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SwissFranc(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-swiss-franc'], 'items': [{'path': {'d': 'M10 21V3h8'}}, {'path': {'d': 'M6 16h9'}}, {'path': {'d': 'M10 9.5h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
