
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def DoorClosedLocked(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-door-closed-locked'], 'items': [{'path': {'d': 'M10 12h.01'}}, {'path': {'d': 'M18 9V6a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v14'}}, {'path': {'d': 'M2 20h8'}}, {'path': {'d': 'M20 17v-2a2 2 0 1 0-4 0v2'}}, {'rect': {'x': '14', 'y': '17', 'width': '8', 'height': '5', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
