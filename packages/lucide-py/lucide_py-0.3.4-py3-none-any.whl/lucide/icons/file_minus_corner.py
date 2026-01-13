
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def FileMinusCorner(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-file-minus-corner'], 'items': [{'path': {'d': 'M20 14V8a2.4 2.4 0 0 0-.706-1.706l-3.588-3.588A2.4 2.4 0 0 0 14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12'}}, {'path': {'d': 'M14 2v5a1 1 0 0 0 1 1h5'}}, {'path': {'d': 'M14 18h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
