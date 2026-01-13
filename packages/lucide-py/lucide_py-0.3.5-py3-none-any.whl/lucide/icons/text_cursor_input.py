
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TextCursorInput(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-text-cursor-input'], 'items': [{'path': {'d': 'M12 20h-1a2 2 0 0 1-2-2 2 2 0 0 1-2 2H6'}}, {'path': {'d': 'M13 8h7a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-7'}}, {'path': {'d': 'M5 16H4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h1'}}, {'path': {'d': 'M6 4h1a2 2 0 0 1 2 2 2 2 0 0 1 2-2h1'}}, {'path': {'d': 'M9 6v12'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
