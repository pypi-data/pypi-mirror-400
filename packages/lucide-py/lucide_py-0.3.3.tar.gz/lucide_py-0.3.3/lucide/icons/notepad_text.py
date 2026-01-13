
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def NotepadText(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-notepad-text'], 'items': [{'path': {'d': 'M8 2v4'}}, {'path': {'d': 'M12 2v4'}}, {'path': {'d': 'M16 2v4'}}, {'rect': {'width': '16', 'height': '18', 'x': '4', 'y': '4', 'rx': '2'}}, {'path': {'d': 'M8 10h6'}}, {'path': {'d': 'M8 14h8'}}, {'path': {'d': 'M8 18h5'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
