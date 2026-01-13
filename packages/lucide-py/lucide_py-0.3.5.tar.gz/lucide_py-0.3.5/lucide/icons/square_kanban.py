
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SquareKanban(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-square-kanban'], 'items': [{'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}, {'path': {'d': 'M8 7v7'}}, {'path': {'d': 'M12 7v4'}}, {'path': {'d': 'M16 7v9'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
