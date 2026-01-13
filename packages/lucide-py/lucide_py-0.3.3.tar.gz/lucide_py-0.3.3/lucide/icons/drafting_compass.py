
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def DraftingCompass(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-drafting-compass'], 'items': [{'path': {'d': 'm12.99 6.74 1.93 3.44'}}, {'path': {'d': 'M19.136 12a10 10 0 0 1-14.271 0'}}, {'path': {'d': 'm21 21-2.16-3.84'}}, {'path': {'d': 'm3 21 8.02-14.26'}}, {'circle': {'cx': '12', 'cy': '5', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
