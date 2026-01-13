import json

from utcnow import utcnow

from .context import Context
from .models.enum import PlotType
from .utils.period import find_range_interval


def output(ctx: Context):
    result = {}

    plot_data = ctx.plots()
    signal_data = ctx.signals()

    result[PlotType.HISTOGRAM.value] = [
        {
            "label": plot.label,
            "data": [item.to_dict() for item in plot.data],
            "screen_index": plot.screen_index,
        }
        for plot in plot_data.get(PlotType.HISTOGRAM.value, [])
    ]

    result[PlotType.LINE.value] = [
        {
            "label": plot.label,
            "data": [item.to_dict() for item in plot.data],
            "screen_index": plot.screen_index,
        }
        for plot in plot_data.get(PlotType.LINE.value, [])
    ]

    result[PlotType.AREA.value] = [
        {
            "label": plot.label,
            "data": [item.to_dict() for item in plot.data],
            "screen_index": plot.screen_index,
        }
        for plot in plot_data.get(PlotType.AREA.value, [])
    ]

    result["strategy"] = [
        {
            "label": "default",
            "data": [item.to_dict() for item in signal_data],
        }
    ]

    result["quotes"] = {
        "ticker": ctx.symbol(),
        "interval": find_range_interval(ctx.period()).interval,
        "provider": ctx.provider().source(),
        "data": [
            {
                "timestamp": utcnow.get(quote.timestamp.isoformat()),
                "open": quote.open,
                "high": quote.high,
                "low": quote.low,
                "close": quote.close,
                "volume": quote.volume,
            }
            for quote in ctx.quotes()
        ],
    }

    print(json.dumps(result))
