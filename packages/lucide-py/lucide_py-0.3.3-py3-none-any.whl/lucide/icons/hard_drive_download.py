
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def HardDriveDownload(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-hard-drive-download'], 'items': [{'path': {'d': 'M12 2v8'}}, {'path': {'d': 'm16 6-4 4-4-4'}}, {'rect': {'width': '20', 'height': '8', 'x': '2', 'y': '14', 'rx': '2'}}, {'path': {'d': 'M6 18h.01'}}, {'path': {'d': 'M10 18h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
