
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def BanknoteArrowDown(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-banknote-arrow-down'], 'items': [{'path': {'d': 'M12 18H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5'}}, {'path': {'d': 'm16 19 3 3 3-3'}}, {'path': {'d': 'M18 12h.01'}}, {'path': {'d': 'M19 16v6'}}, {'path': {'d': 'M6 12h.01'}}, {'circle': {'cx': '12', 'cy': '12', 'r': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
