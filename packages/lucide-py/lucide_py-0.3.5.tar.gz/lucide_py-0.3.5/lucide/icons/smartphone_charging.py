
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def SmartphoneCharging(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-smartphone-charging'], 'items': [{'rect': {'width': '14', 'height': '20', 'x': '5', 'y': '2', 'rx': '2', 'ry': '2'}}, {'path': {'d': 'M12.667 8 10 12h4l-2.667 4'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
