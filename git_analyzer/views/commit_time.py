"""View for displaying commits by hour of day."""

from textual.reactive import reactive
from textual_plotext import PlotextPlot

from .base import BaseView


class CommitTimeView(BaseView):
    """A view to display commit time distribution."""

    title = reactive("Commits by Hour")
    data = reactive({})

    DEFAULT_CSS = """
    CommitTimeView {
        width: 100%;
        height: 100%;
    }

    PlotextPlot {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(self):
        super().__init__()
        self.plot_widget = PlotextPlot()

    def compose(self):
        """Set up the initial plot."""
        yield self.plot_widget

    def watch_data(self, value) -> None:
        """React to data changes."""
        self.refresh_chart()

    def refresh_chart(self) -> None:
        """Refresh the chart with current data."""
        self.plot()

    def on_mount(self) -> None:
        """Handle the mount event."""
        self.plot()

    async def on_resize(self, event) -> None:
        """Handle resize events to update the plot size."""
        self.plot()

    def plot(self) -> None:
        """Plot the commit time data."""
        plt = self.plot_widget.plt
        plt.clear_figure()
        plt.theme("dark")

        # Set the plot size based on container size
        available_width = max(10, self.size.width - 2)  # Minimum width of 10
        available_height = max(10, self.size.height - 2)  # Minimum height of 10
        plt.plotsize(available_width, available_height)

        plt.title(self.title)
        plt.xlabel("Hour (24h format)")
        plt.ylabel("Number of Commits")

        if not self.data:
            return

        hours = list(range(24))
        counts = [self.data.get(hour, 0) for hour in hours]

        if any(counts):  # Only plot if we have data
            # Create x-axis positions
            x_positions = [float(x) for x in hours]

            # Plot the bars
            plt.bar(x_positions, counts, width=0.5)

            # Set x-axis ticks for every 3 hours
            tick_positions = [float(x) for x in range(0, 24, 3)]
            tick_labels = [str(h) for h in range(0, 24, 3)]
            plt.xticks(tick_positions, tick_labels)

        self.plot_widget.refresh()

    async def load_data(self, git_data) -> None:
        """Load commit time data."""
        self.is_loading = True
        try:
            self.data = git_data.get_commits_by_hour()
        finally:
            self.is_loading = False

    def clear_data(self) -> None:
        """Clear the view's data."""
        self.data = {}
