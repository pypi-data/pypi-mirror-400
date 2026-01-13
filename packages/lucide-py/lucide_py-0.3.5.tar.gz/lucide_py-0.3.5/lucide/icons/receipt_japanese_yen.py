
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ReceiptJapaneseYen(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-receipt-japanese-yen'], 'items': [{'path': {'d': 'M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z'}}, {'path': {'d': 'm12 10 3-3'}}, {'path': {'d': 'm9 7 3 3v7.5'}}, {'path': {'d': 'M9 11h6'}}, {'path': {'d': 'M9 15h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
