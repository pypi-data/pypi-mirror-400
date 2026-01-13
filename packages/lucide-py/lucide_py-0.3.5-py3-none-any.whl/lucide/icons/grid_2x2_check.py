
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Grid2x2Check(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-grid-2x2-check'], 'items': [{'path': {'d': 'M12 3v17a1 1 0 0 1-1 1H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6a1 1 0 0 1-1 1H3'}}, {'path': {'d': 'm16 19 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
