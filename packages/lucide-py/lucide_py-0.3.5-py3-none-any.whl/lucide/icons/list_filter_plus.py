
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ListFilterPlus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-list-filter-plus'], 'items': [{'path': {'d': 'M12 5H2'}}, {'path': {'d': 'M6 12h12'}}, {'path': {'d': 'M9 19h6'}}, {'path': {'d': 'M16 5h6'}}, {'path': {'d': 'M19 8V2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
