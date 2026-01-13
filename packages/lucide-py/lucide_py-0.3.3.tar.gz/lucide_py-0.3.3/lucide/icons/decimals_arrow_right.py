
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def DecimalsArrowRight(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-decimals-arrow-right'], 'items': [{'path': {'d': 'M10 18h10'}}, {'path': {'d': 'm17 21 3-3-3-3'}}, {'path': {'d': 'M3 11h.01'}}, {'rect': {'x': '15', 'y': '3', 'width': '5', 'height': '8', 'rx': '2.5'}}, {'rect': {'x': '6', 'y': '3', 'width': '5', 'height': '8', 'rx': '2.5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
