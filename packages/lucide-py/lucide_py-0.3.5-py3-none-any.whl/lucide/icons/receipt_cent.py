
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ReceiptCent(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-receipt-cent'], 'items': [{'path': {'d': 'M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z'}}, {'path': {'d': 'M12 6.5v11'}}, {'path': {'d': 'M15 9.4a4 4 0 1 0 0 5.2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
