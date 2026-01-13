
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ReceiptPoundSterling(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-receipt-pound-sterling'], 'items': [{'path': {'d': 'M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z'}}, {'path': {'d': 'M8 13h5'}}, {'path': {'d': 'M10 17V9.5a2.5 2.5 0 0 1 5 0'}}, {'path': {'d': 'M8 17h7'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
