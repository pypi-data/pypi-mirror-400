
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Grid2x2Plus(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-grid-2x2-plus'], 'items': [{'path': {'d': 'M12 3v17a1 1 0 0 1-1 1H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6a1 1 0 0 1-1 1H3'}}, {'path': {'d': 'M16 19h6'}}, {'path': {'d': 'M19 22v-6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
