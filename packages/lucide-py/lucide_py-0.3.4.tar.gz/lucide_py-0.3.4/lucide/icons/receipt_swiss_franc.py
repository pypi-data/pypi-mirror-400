
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ReceiptSwissFranc(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-receipt-swiss-franc'], 'items': [{'path': {'d': 'M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z'}}, {'path': {'d': 'M10 17V7h5'}}, {'path': {'d': 'M10 11h4'}}, {'path': {'d': 'M8 15h5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
