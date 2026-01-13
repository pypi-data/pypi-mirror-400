
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ArrowDownWideNarrow(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-arrow-down-wide-narrow'], 'items': [{'path': {'d': 'm3 16 4 4 4-4'}}, {'path': {'d': 'M7 20V4'}}, {'path': {'d': 'M11 4h10'}}, {'path': {'d': 'M11 8h7'}}, {'path': {'d': 'M11 12h4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
