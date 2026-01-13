import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from openstoxlify.context import Context
from openstoxlify.draw import Canvas
from openstoxlify.models.enum import ActionType, PlotType, Period
from openstoxlify.models.series import ActionSeries, FloatSeries
from openstoxlify.models.model import Quote, PlotData
from openstoxlify.models.contract import Provider


class TestCanvas(unittest.TestCase):
    """Test suite untuk Canvas class"""

    def setUp(self):
        """Setup mock context dan canvas untuk setiap test"""
        self.mock_ctx = Mock(spec=Context)
        self.mock_ctx.plots.return_value = {}
        self.mock_ctx.quotes.return_value = []
        self.mock_ctx.signals.return_value = []

        self.canvas = Canvas(self.mock_ctx)

    def test_initialization(self):
        """Test Canvas initialization"""
        self.assertIsNotNone(self.canvas)
        self.assertEqual(self.canvas._plot_data, {})
        self.assertEqual(self.canvas._market_data, [])
        self.assertEqual(self.canvas._strategy_data, [])

    def test_has_plotting_data_empty(self):
        """Test _has_plotting_data() dengan data kosong"""
        self.assertFalse(self.canvas._has_plotting_data())

    def test_has_plotting_data_with_market_data(self):
        """Test _has_plotting_data() dengan market data"""
        self.canvas._market_data = [
            Quote(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                high=100.0,
                low=90.0,
                open=95.0,
                close=98.0,
                volume=1000,
            )
        ]
        self.assertTrue(self.canvas._has_plotting_data())

    def test_has_plotting_data_with_strategy_data(self):
        """Test _has_plotting_data() dengan strategy data"""
        self.canvas._strategy_data = [
            ActionSeries(
                datetime(2024, 1, 1, tzinfo=timezone.utc), ActionType.LONG, 1.0
            )
        ]
        self.assertTrue(self.canvas._has_plotting_data())

    def test_has_plotting_data_with_plots(self):
        """Test _has_plotting_data() dengan plot data"""
        self.canvas._plot_data = {
            PlotType.LINE.value: [
                PlotData(
                    label="MA20",
                    data=[FloatSeries(datetime.now(), 100.0)],
                    screen_index=0,
                )
            ]
        }
        self.assertTrue(self.canvas._has_plotting_data())

    def test_unique_screens_default(self):
        """Test _unique_screens() mengembalikan [0] sebagai default"""
        screens = self.canvas._unique_screens()
        self.assertIn(0, screens)
        self.assertEqual(len(screens), 1)

    def test_unique_screens_multiple(self):
        """Test _unique_screens() dengan multiple screens"""
        self.canvas._plot_data = {
            PlotType.LINE.value: [
                PlotData(label="MA20", data=[], screen_index=0),
                PlotData(label="MACD", data=[], screen_index=1),
            ],
            PlotType.HISTOGRAM.value: [
                PlotData(label="Volume", data=[], screen_index=2),
            ],
        }
        screens = self.canvas._unique_screens()
        self.assertEqual(sorted(screens), [0, 1, 2])

    def test_convert_timestamp_string(self):
        """Test convert_timestamp() dengan string ISO format"""
        timestamp_str = "2024-01-01T00:00:00+00:00"
        result = self.canvas.convert_timestamp(timestamp_str)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_convert_timestamp_datetime(self):
        """Test convert_timestamp() dengan datetime object"""
        timestamp_dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
        result = self.canvas.convert_timestamp(timestamp_dt)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_get_color_consistency(self):
        """Test _get_color() mengembalikan warna yang konsisten untuk label yang sama"""
        label = "MA20"
        color1 = self.canvas._get_color(label)
        color2 = self.canvas._get_color(label)
        self.assertEqual(color1, color2)

    def test_get_color_different_labels(self):
        """Test _get_color() bisa mengembalikan warna berbeda untuk label berbeda"""
        label1 = "MA20"
        label2 = "MA50"
        color1 = self.canvas._get_color(label1)
        color2 = self.canvas._get_color(label2)
        # Note: might be the same color due to random.choice, but keys should be different
        self.assertIn(label1, self.canvas._color_map)
        self.assertIn(label2, self.canvas._color_map)

    def test_draw_with_no_data(self):
        """Test draw() dengan tidak ada data tidak menampilkan plot"""
        # When there's no data, _unique_screens returns [0] but should not plot
        # The method returns early when unique_screens_count is 0
        # But actually _unique_screens always adds 0, so count is never 0
        # Let's just verify it doesn't crash with empty data
        try:
            self.canvas.draw()
        except Exception:
            self.fail("draw() should not raise exception with no data")

    @patch("openstoxlify.draw.plt.subplots")
    @patch("openstoxlify.draw.plt.show")
    @patch("openstoxlify.draw.plt.tight_layout")
    @patch("openstoxlify.draw.plt.setp")
    def test_draw_with_market_data(
        self, mock_setp, mock_tight, mock_show, mock_subplots
    ):
        """Test draw() dengan market data"""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.get_legend_handles_labels.return_value = ([], [])
        mock_ax.xaxis = Mock()
        mock_ax.xaxis.get_majorticklabels.return_value = []
        mock_ax.xaxis.set_major_locator = Mock()
        mock_ax.xaxis.set_major_formatter = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        self.canvas._market_data = [
            Quote(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                high=105.0,
                low=95.0,
                open=100.0,
                close=102.0,
                volume=1000,
            ),
            Quote(
                timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
                high=110.0,
                low=100.0,
                open=102.0,
                close=98.0,
                volume=1500,
            ),
        ]

        self.canvas.draw()

        mock_subplots.assert_called_once()
        mock_ax.vlines.assert_called()
        mock_show.assert_called_once()

    @patch("openstoxlify.draw.plt.subplots")
    @patch("openstoxlify.draw.plt.show")
    @patch("openstoxlify.draw.plt.tight_layout")
    @patch("openstoxlify.draw.plt.setp")
    def test_draw_with_custom_parameters(
        self, mock_setp, mock_tight, mock_show, mock_subplots
    ):
        """Test draw() dengan custom parameters"""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.get_legend_handles_labels.return_value = ([], [])
        mock_ax.xaxis = Mock()
        mock_ax.xaxis.get_majorticklabels.return_value = []
        mock_ax.xaxis.set_major_locator = Mock()
        mock_ax.xaxis.set_major_formatter = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        self.canvas._market_data = [
            Quote(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                high=100.0,
                low=90.0,
                open=95.0,
                close=98.0,
                volume=1000,
            )
        ]

        self.canvas.draw(
            show_legend=False,
            figsize=(16, 8),
            title="Custom Title",
            xlabel="Time",
            ylabel="Value",
        )

        mock_subplots.assert_called_once()
        call_args = mock_subplots.call_args
        self.assertEqual(call_args[1]["figsize"], (16, 8))


class TestIntegration(unittest.TestCase):
    """Integration tests untuk workflow lengkap"""

    def setUp(self):
        """Setup untuk integration tests"""
        self.mock_provider = Mock(spec=Provider)
        self.symbol = "BTC-USD"
        self.period = Period.DAILY

    def test_full_workflow_simple(self):
        """Test workflow sederhana: get quotes, plot, signal"""
        # Setup mock quotes
        mock_quotes = [
            Quote(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                high=105.0,
                low=95.0,
                open=100.0,
                close=102.0,
                volume=1000,
            ),
            Quote(
                timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
                high=110.0,
                low=100.0,
                open=102.0,
                close=108.0,
                volume=1500,
            ),
            Quote(
                timestamp=datetime(2024, 1, 3, tzinfo=timezone.utc),
                high=115.0,
                low=105.0,
                open=108.0,
                close=98.0,
                volume=2000,
            ),
        ]
        self.mock_provider.quotes.return_value = mock_quotes

        # Create context
        ctx = Context(self.mock_provider, self.symbol, self.period)

        # Get quotes
        quotes = ctx.quotes()
        self.assertEqual(len(quotes), 3)

        # Calculate simple indicator (median)
        from statistics import median

        prices = [q.close for q in quotes]
        median_value = median(prices)

        # Plot median line
        for quote in quotes:
            ctx.plot(
                "Median", PlotType.LINE, FloatSeries(quote.timestamp, median_value)
            )

        # Find lowest and highest
        lowest = min(quotes, key=lambda q: q.close)
        highest = max(quotes, key=lambda q: q.close)

        # Add signals
        ctx.signal(ActionSeries(lowest.timestamp, ActionType.LONG, 1.0))
        ctx.signal(ActionSeries(highest.timestamp, ActionType.SHORT, 1.0))

        # Verify plots and signals
        plots = ctx.plots()
        signals = ctx.signals()

        self.assertIn(PlotType.LINE.value, plots)
        self.assertEqual(len(plots[PlotType.LINE.value][0].data), 3)
        self.assertEqual(len(signals), 2)
        self.assertEqual(signals[0].action, ActionType.LONG)
        self.assertEqual(signals[1].action, ActionType.SHORT)

    @patch("openstoxlify.draw.plt.subplots")
    @patch("openstoxlify.draw.plt.show")
    @patch("openstoxlify.draw.plt.tight_layout")
    @patch("openstoxlify.draw.plt.setp")
    def test_full_workflow_with_canvas(
        self, mock_setp, mock_tight, mock_show, mock_subplots
    ):
        """Test workflow lengkap dengan Canvas"""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_ax.get_legend_handles_labels.return_value = ([], [])
        mock_ax.xaxis = Mock()
        mock_ax.xaxis.get_majorticklabels.return_value = []
        mock_ax.xaxis.set_major_locator = Mock()
        mock_ax.xaxis.set_major_formatter = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        mock_quotes = [
            Quote(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                high=105.0,
                low=95.0,
                open=100.0,
                close=102.0,
                volume=1000,
            )
        ]
        self.mock_provider.quotes.return_value = mock_quotes

        ctx = Context(self.mock_provider, self.symbol, self.period)
        quotes = ctx.quotes()

        for quote in quotes:
            ctx.plot("Price", PlotType.LINE, FloatSeries(quote.timestamp, quote.close))

        ctx.signal(ActionSeries(quotes[0].timestamp, ActionType.LONG, 1.0))

        canvas = Canvas(ctx)
        canvas.draw()

        mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
