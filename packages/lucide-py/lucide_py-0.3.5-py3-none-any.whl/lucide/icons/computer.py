
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Computer(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-computer'], 'items': [{'rect': {'width': '14', 'height': '8', 'x': '5', 'y': '2', 'rx': '2'}}, {'rect': {'width': '20', 'height': '8', 'x': '2', 'y': '14', 'rx': '2'}}, {'path': {'d': 'M6 18h2'}}, {'path': {'d': 'M12 18h6'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
