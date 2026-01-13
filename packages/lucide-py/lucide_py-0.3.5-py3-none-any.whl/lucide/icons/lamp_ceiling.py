
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def LampCeiling(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-lamp-ceiling'], 'items': [{'path': {'d': 'M12 2v5'}}, {'path': {'d': 'M14.829 15.998a3 3 0 1 1-5.658 0'}}, {'path': {'d': 'M20.92 14.606A1 1 0 0 1 20 16H4a1 1 0 0 1-.92-1.394l3-7A1 1 0 0 1 7 7h10a1 1 0 0 1 .92.606z'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
