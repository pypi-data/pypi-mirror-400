
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ShoppingBasket(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-shopping-basket'], 'items': [{'path': {'d': 'm15 11-1 9'}}, {'path': {'d': 'm19 11-4-7'}}, {'path': {'d': 'M2 11h20'}}, {'path': {'d': 'm3.5 11 1.6 7.4a2 2 0 0 0 2 1.6h9.8a2 2 0 0 0 2-1.6l1.7-7.4'}}, {'path': {'d': 'M4.5 15.5h15'}}, {'path': {'d': 'm5 11 4-7'}}, {'path': {'d': 'm9 11 1 9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
