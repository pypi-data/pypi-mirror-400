
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def Notebook(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-notebook'], 'items': [{'path': {'d': 'M2 6h4'}}, {'path': {'d': 'M2 10h4'}}, {'path': {'d': 'M2 14h4'}}, {'path': {'d': 'M2 18h4'}}, {'rect': {'width': '16', 'height': '20', 'x': '4', 'y': '2', 'rx': '2'}}, {'path': {'d': 'M16 2v20'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
