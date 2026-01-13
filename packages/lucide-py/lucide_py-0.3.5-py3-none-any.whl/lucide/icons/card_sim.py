
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def CardSim(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-card-sim'], 'items': [{'path': {'d': 'M12 14v4'}}, {'path': {'d': 'M14.172 2a2 2 0 0 1 1.414.586l3.828 3.828A2 2 0 0 1 20 7.828V20a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z'}}, {'path': {'d': 'M8 14h8'}}, {'rect': {'x': '8', 'y': '10', 'width': '8', 'height': '8', 'rx': '1'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
