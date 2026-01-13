from typing import List, Protocol, runtime_checkable

from .series import ActionSeries
from .model import Quote
from .enum import Period


@runtime_checkable
class Provider(Protocol):
    def source(self) -> str: ...

    def quotes(self, symbol: str, period: Period) -> List[Quote]: ...

    def authenticate(self, token: str) -> None: ...

    def execute(
        self, id: str, symbol: str, action: ActionSeries, amount: float
    ) -> None: ...
