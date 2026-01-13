
import contextlib
from collections.abc import Generator

from .base import IconBase

                        
@contextlib.contextmanager
def WalletMinimal(**kwargs) -> Generator[None]:
    data = {'classes': ['lucide lucide-wallet-minimal'], 'items': [{'path': {'d': 'M17 14h.01'}}, {'path': {'d': 'M7 7h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14'}}]}
    with IconBase(data, **kwargs):
        pass
    yield
