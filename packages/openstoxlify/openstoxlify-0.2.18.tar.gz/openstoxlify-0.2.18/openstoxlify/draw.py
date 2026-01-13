import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from typing import Dict, List
from datetime import datetime

from .context import Context
from .utils.color import color_palette
from .models.enum import PlotType, ActionType


class Canvas:
    """
    Professional financial chart renderer.

    The Canvas class generates multi-panel matplotlib charts combining:
    - OHLC candlestick charts
    - Technical indicators (lines, histograms, areas)
    - Trading signal markers and annotations
    - Multiple subplot panels with independent scales

    Attributes:
        _plot_data (Dict): Indicator data organized by plot type
        _market_data (List[Quote]): OHLCV market quotes
        _strategy_data (List[ActionSeries]): Trading signals
        _color_map (Dict[str, str]): Label-to-color mapping for consistency

    Example:
        >>> canvas = Canvas(ctx)
        >>> canvas.draw(
        ...     figsize=(16, 9),
        ...     title="My Trading Strategy",
        ...     show_legend=True
        ... )
    """

    def __init__(self, ctx: Context):
        """
        Initialize canvas from trading context.

        Args:
            ctx (Context): Trading context containing market data, plots,
                and signals

        Example:
            >>> provider = Provider(DefaultProvider.YFinance)
            >>> ctx = Context(provider, "AAPL", Period.DAILY)
            >>> canvas = Canvas(ctx)
        """
        self._plot_data = ctx.plots()
        self._market_data = ctx.quotes()
        self._strategy_data = ctx.signals()

        self._color_map: Dict[str, str] = {}

    def _get_color(self, label):
        """
        Get or assign a consistent color for a label.

        Colors are randomly assigned from the palette and cached to ensure
        the same label always gets the same color across the chart.

        Args:
            label (str): Indicator label (e.g., "SMA 20")

        Returns:
            str: Hex color code (e.g., "#FF5733")

        Note:
            Uses color_palette() from utils.color for predefined colors.
        """
        opts = color_palette()
        if label not in self._color_map:
            self._color_map[label] = random.choice(opts)
        return self._color_map[label]

    def _has_plotting_data(self) -> bool:
        """
        Check if there's any data to plot.

        Returns:
            bool: True if market data, signals, or plot data exists

        Note:
            Used internally to determine if chart rendering should proceed.
        """
        return (
            len(self._market_data) > 0
            or len(self._strategy_data) > 0
            or any(self._plot_data.get(pt.value) for pt in PlotType)
        )

    def _unique_screens(self) -> List[int]:
        """
        Identify unique screen indices from plot data.

        Scans all plot data to find which screen indices are used,
        ensuring screen 0 (main chart) is always included.

        Returns:
            List[int]: Sorted list of screen indices (e.g., [0, 1, 2])

        Example:
            >>> # If plots use screen_index 0, 1, 2
            >>> canvas._unique_screens()
            [0, 1, 2]

        Note:
            Screen 0 is always included even if no plots explicitly use it,
            as it's reserved for the main price chart.
        """
        screens = {
            item.screen_index
            for plot_type in (PlotType.HISTOGRAM, PlotType.LINE, PlotType.AREA)
            for item in self._plot_data.get(plot_type.value, [])
        }
        screens.add(0)
        return sorted(screens)

    def convert_timestamp(self, timestamp):
        """
        Convert timestamp to matplotlib date number.

        Handles both string (ISO format) and datetime objects, converting
        them to matplotlib's internal date representation for plotting.

        Args:
            timestamp: Either datetime object or ISO format string

        Returns:
            float: Matplotlib date number

        Example:
            >>> ts_str = "2024-01-01T00:00:00+00:00"
            >>> num = canvas.convert_timestamp(ts_str)
            >>> # Use num for matplotlib plotting

        Note:
            Matplotlib uses a float-based date system where the integer
            part is days since 0001-01-01 UTC.
        """
        if isinstance(timestamp, str):
            return float(mdates.date2num(datetime.fromisoformat(timestamp)))
        return float(mdates.date2num(timestamp))

    def draw(
        self,
        show_legend: bool = True,
        figsize: tuple = (12, 6),
        offset_multiplier: float = 0.05,
        rotation: int = 30,
        ha: str = "right",
        title: str = "Market Data Visualizations",
        xlabel: str = "Date",
        ylabel: str = "Price",
        candle_linewidth: float = 1,
        candle_body_width: float = 4,
        marker_size: int = 8,
        annotation_fontsize: int = 9,
        histogram_alpha: float = 0.6,
        area_alpha: float = 0.3,
        line_width: float = 2,
    ):
        """
        Render the complete financial chart.

        Creates a professional multi-panel chart with candlesticks,
        indicators, and trading signals. Automatically handles subplot
        layout based on screen indices used in plot data.

        Args:
            show_legend (bool): Whether to show the legend. Default True.
            figsize (tuple): Figure size as (width, height). Default (12, 6).
            offset_multiplier (float): Multiplier for trade annotation offset
                from price. Default 0.05 (5% of price).
            rotation (int): Rotation angle for x-axis labels. Default 30.
            ha (str): Horizontal alignment for x-axis labels ('left', 'center',
                'right'). Default 'right'.
            title (str): Chart title. Default 'Market Data Visualizations'.
            xlabel (str): X-axis label. Default 'Date'.
            ylabel (str): Y-axis label for main chart. Default 'Price'.
            candle_linewidth (float): Width of candlestick wick lines. Default 1.
            candle_body_width (float): Width of candlestick body lines. Default 4.
            marker_size (int): Size of trade signal markers. Default 8.
            annotation_fontsize (int): Font size for trade annotations. Default 9.
            histogram_alpha (float): Transparency for histogram bars (0-1).
                Default 0.6.
            area_alpha (float): Transparency for area plots (0-1). Default 0.3.
            line_width (float): Width of line plots. Default 2.

        Example:
            >>> # Basic usage
            >>> canvas.draw()
            >>>
            >>> # Customized for presentation
            >>> canvas.draw(
            ...     figsize=(16, 9),
            ...     title="Bitcoin Trading Strategy",
            ...     candle_body_width=6,
            ...     marker_size=12,
            ...     line_width=2.5
            ... )

        Note:
            - Screen 0 is reserved for the main price chart with candlesticks
            - Additional screens (1, 2, 3...) create separate subplot panels
            - Each subplot has its own y-axis scale
            - Long signals appear as blue upward triangles
            - Short signals appear as purple downward triangles
        """
        screens = self._unique_screens()
        unique_screens_count = len(screens)

        if unique_screens_count == 0:
            return

        if unique_screens_count == 1:
            fig, ax = plt.subplots(figsize=figsize)
            axes = {screens[0]: ax}
        else:
            fig, axes_array = plt.subplots(
                unique_screens_count, 1, figsize=figsize, sharex=True, squeeze=False
            )
            axes_array = axes_array.flatten()
            axes = {screen_idx: axes_array[i] for i, screen_idx in enumerate(screens)}

        plotted_histograms = set()
        for plot in self._plot_data.get(PlotType.HISTOGRAM.value, []):
            screen_idx = plot.screen_index

            if screen_idx not in axes:
                continue

            ax = axes[screen_idx]

            timestamps = [self.convert_timestamp(item.timestamp) for item in plot.data]
            values = [item.value for item in plot.data]

            bar_width = (
                (max(timestamps) - min(timestamps)) / len(timestamps) * 0.8
                if len(timestamps) > 1
                else 0.5
            )
            label = plot.label if plot.label not in plotted_histograms else "_nolegend_"
            plotted_histograms.add(plot.label)

            ax.bar(
                timestamps,
                values,
                label=label,
                color=self._get_color(plot.label),
                width=bar_width,
                alpha=histogram_alpha,
            )

        for plot in self._plot_data.get(PlotType.LINE.value, []):
            screen_idx = plot.screen_index
            if screen_idx not in axes:
                continue
            ax = axes[screen_idx]
            timestamps = [self.convert_timestamp(item.timestamp) for item in plot.data]
            values = [item.value for item in plot.data]
            ax.plot(
                timestamps,
                values,
                label=plot.label,
                color=self._get_color(plot.label),
                lw=line_width,
            )

        for plot in self._plot_data.get(PlotType.AREA.value, []):
            screen_idx = plot.screen_index
            if screen_idx not in axes:
                continue
            ax = axes[screen_idx]
            timestamps = [self.convert_timestamp(item.timestamp) for item in plot.data]
            values = [item.value for item in plot.data]
            ax.fill_between(
                timestamps,
                values,
                label=plot.label,
                color=self._get_color(plot.label),
                alpha=area_alpha,
            )

        if 0 in axes:
            ax_main = axes[0]

            candle_lut = {}
            for item in self._market_data:
                timestamp = item.timestamp
                ts_str = (
                    timestamp if isinstance(timestamp, str) else timestamp.isoformat()
                )
                ts_num = self.convert_timestamp(timestamp)
                price = item.close

                color = "green" if item.close > item.open else "red"
                ax_main.vlines(
                    ts_num, item.low, item.high, color=color, lw=candle_linewidth
                )
                ax_main.vlines(
                    ts_num, item.open, item.close, color=color, lw=candle_body_width
                )

                candle_lut[ts_str] = (ts_num, price)

            for trade in self._strategy_data:
                ts_key = (
                    trade.timestamp
                    if isinstance(trade.timestamp, str)
                    else trade.timestamp.isoformat()
                )

                if ts_key not in candle_lut:
                    continue

                ts_num, price = candle_lut[ts_key]
                offset = price * offset_multiplier
                direction = trade.action
                amount = trade.amount

                if direction == ActionType.LONG:
                    y = price - offset
                    ax_main.plot(
                        ts_num, y, marker="^", color="blue", markersize=marker_size
                    )
                    ax_main.annotate(
                        f"LONG {amount}",
                        xy=(ts_num, y),
                        xytext=(0, -15),
                        textcoords="offset points",
                        ha="center",
                        fontsize=annotation_fontsize,
                        color="blue",
                    )
                elif direction == ActionType.SHORT:
                    y = price + offset
                    ax_main.plot(
                        ts_num,
                        y,
                        marker="v",
                        color="purple",
                        markersize=marker_size,
                    )
                    ax_main.annotate(
                        f"SHORT {amount}",
                        xy=(ts_num, y),
                        xytext=(0, 10),
                        textcoords="offset points",
                        ha="center",
                        fontsize=annotation_fontsize,
                        color="purple",
                    )

            ax_main.set_xlabel(xlabel)
            ax_main.set_ylabel(ylabel)
            ax_main.set_title(title)
            if show_legend and ax_main.get_legend_handles_labels()[0]:
                ax_main.legend()

            ax_main.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax_main.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.setp(ax_main.xaxis.get_majorticklabels(), rotation=rotation, ha=ha)

        for screen_idx, ax in axes.items():
            if screen_idx != 0:
                ax.set_ylabel(f"Screen {screen_idx}")
                if show_legend and ax.get_legend_handles_labels()[0]:
                    ax.legend()

        plt.tight_layout()
        plt.show()
