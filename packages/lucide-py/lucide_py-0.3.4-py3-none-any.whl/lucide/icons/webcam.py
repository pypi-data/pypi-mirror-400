
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Webcam(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-webcam'], 'items': [{'circle': {'cx': '12', 'cy': '10', 'r': '8'}}, {'circle': {'cx': '12', 'cy': '10', 'r': '3'}}, {'path': {'d': 'M7 22h10'}}, {'path': {'d': 'M12 22v-4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
