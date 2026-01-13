
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def TvMinimal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-tv-minimal'], 'items': [{'path': {'d': 'M7 21h10'}}, {'rect': {'width': '20', 'height': '14', 'x': '2', 'y': '3', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
