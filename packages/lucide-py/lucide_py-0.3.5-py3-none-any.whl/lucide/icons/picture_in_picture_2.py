
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def PictureInPicture2(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-picture-in-picture-2'], 'items': [{'path': {'d': 'M21 9V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v10c0 1.1.9 2 2 2h4'}}, {'rect': {'width': '10', 'height': '7', 'x': '12', 'y': '13', 'rx': '2'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
