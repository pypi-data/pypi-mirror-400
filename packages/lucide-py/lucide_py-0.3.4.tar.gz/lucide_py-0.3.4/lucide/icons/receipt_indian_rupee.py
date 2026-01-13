
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ReceiptIndianRupee(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-receipt-indian-rupee'], 'items': [{'path': {'d': 'M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z'}}, {'path': {'d': 'M8 7h8'}}, {'path': {'d': 'M12 17.5 8 15h1a4 4 0 0 0 0-8'}}, {'path': {'d': 'M8 11h8'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
