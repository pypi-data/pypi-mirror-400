
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FileCheckCorner(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-file-check-corner'], 'items': [{'path': {'d': 'M10.5 22H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.706.706l3.588 3.588A2.4 2.4 0 0 1 20 8v6'}}, {'path': {'d': 'M14 2v5a1 1 0 0 0 1 1h5'}}, {'path': {'d': 'm14 20 2 2 4-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
