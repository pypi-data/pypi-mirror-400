
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def HardDriveUpload(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-hard-drive-upload'], 'items': [{'path': {'d': 'm16 6-4-4-4 4'}}, {'path': {'d': 'M12 2v8'}}, {'rect': {'width': '20', 'height': '8', 'x': '2', 'y': '14', 'rx': '2'}}, {'path': {'d': 'M6 18h.01'}}, {'path': {'d': 'M10 18h.01'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
