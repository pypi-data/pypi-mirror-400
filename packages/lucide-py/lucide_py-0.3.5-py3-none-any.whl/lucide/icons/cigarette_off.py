
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CigaretteOff(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-cigarette-off'], 'items': [{'path': {'d': 'M12 12H3a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h13'}}, {'path': {'d': 'M18 8c0-2.5-2-2.5-2-5'}}, {'path': {'d': 'm2 2 20 20'}}, {'path': {'d': 'M21 12a1 1 0 0 1 1 1v2a1 1 0 0 1-.5.866'}}, {'path': {'d': 'M22 8c0-2.5-2-2.5-2-5'}}, {'path': {'d': 'M7 12v4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
