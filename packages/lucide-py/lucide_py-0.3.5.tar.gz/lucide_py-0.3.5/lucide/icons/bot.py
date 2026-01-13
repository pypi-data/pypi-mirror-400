
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Bot(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-bot'], 'items': [{'path': {'d': 'M12 8V4H8'}}, {'rect': {'width': '16', 'height': '12', 'x': '4', 'y': '8', 'rx': '2'}}, {'path': {'d': 'M2 14h2'}}, {'path': {'d': 'M20 14h2'}}, {'path': {'d': 'M15 13v2'}}, {'path': {'d': 'M9 13v2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
