
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Wallpaper(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-wallpaper'], 'items': [{'path': {'d': 'M12 17v4'}}, {'path': {'d': 'M8 21h8'}}, {'path': {'d': 'm9 17 6.1-6.1a2 2 0 0 1 2.81.01L22 15'}}, {'circle': {'cx': '8', 'cy': '9', 'r': '2'}}, {'rect': {'x': '2', 'y': '3', 'width': '20', 'height': '14', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
