
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TableCellsSplit(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-table-cells-split'], 'items': [{'path': {'d': 'M12 15V9'}}, {'path': {'d': 'M3 15h18'}}, {'path': {'d': 'M3 9h18'}}, {'rect': {'width': '18', 'height': '18', 'x': '3', 'y': '3', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
