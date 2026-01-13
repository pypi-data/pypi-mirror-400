
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ReceiptTurkishLira(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-receipt-turkish-lira'], 'items': [{'path': {'d': 'M10 6.5v11a5.5 5.5 0 0 0 5.5-5.5'}}, {'path': {'d': 'm14 8-6 3'}}, {'path': {'d': 'M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
