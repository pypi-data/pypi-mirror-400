
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def ParkingMeter(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-parking-meter'], 'items': [{'path': {'d': 'M11 15h2'}}, {'path': {'d': 'M12 12v3'}}, {'path': {'d': 'M12 19v3'}}, {'path': {'d': 'M15.282 19a1 1 0 0 0 .948-.68l2.37-6.988a7 7 0 1 0-13.2 0l2.37 6.988a1 1 0 0 0 .948.68z'}}, {'path': {'d': 'M9 9a3 3 0 1 1 6 0'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
