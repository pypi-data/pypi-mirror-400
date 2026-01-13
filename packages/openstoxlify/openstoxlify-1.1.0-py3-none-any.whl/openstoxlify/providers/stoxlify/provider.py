# pyright: reportAttributeAccessIssue=false
from datetime import timezone
from typing import List

from .proto import client
from .proto.market import market_pb2, market_pb2_grpc

from ...utils.period import find_range_interval
from ...models.enum import DefaultProvider, Period
from ...models.series import ActionSeries
from ...models.model import Quote


class Provider:
    def __init__(self, source: DefaultProvider):
        self._source = source

    def source(self) -> str:
        return self._source.value

    def quotes(self, symbol: str, period: Period) -> List[Quote]:
        range_interval = find_range_interval(period)
        try:
            c = client.channel()
            stub = market_pb2_grpc.MarketServiceStub(c)
            req = market_pb2.GetProductInfoRequest(
                Ticker=symbol,
                Range=range_interval.range,
                Interval=range_interval.interval,
                Indicator="quote",
                Source=self._source.value,
            )
            response = stub.GetProductInfo(req)
        except Exception as err:
            raise RuntimeError(f"request failed: {err}") from err

        quotes = []
        for q in response.Quote:
            ts = q.Timestamp.ToDatetime().replace(tzinfo=timezone.utc)
            price = q.ProductInfo.Price
            quotes.append(
                Quote(
                    timestamp=ts,
                    high=price.High,
                    low=price.Low,
                    open=price.Open,
                    close=price.Close,
                    volume=price.Volume,
                )
            )
        return quotes

    def authenticate(self, token: str) -> None:
        self._token = token
        return

    def execute(self, symbol: str, action: ActionSeries, amount: float) -> None:
        return
