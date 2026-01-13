
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Dock(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-dock'], 'items': [{'path': {'d': 'M2 8h20'}}, {'rect': {'width': '20', 'height': '16', 'x': '2', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M6 16h12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
