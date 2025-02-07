"""View for displaying commits by author."""

from textual.reactive import reactive
from textual_plotext import PlotextPlot

from .base import BaseView


class AuthorCommitsView(BaseView):
    """A view to display commit distribution by author."""

    title = reactive("Commits by Author")
    data = reactive({})
    git_command = reactive("git shortlog -sn --all")

    DEFAULT_CSS = """
    AuthorCommitsView {
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
        """Plot the author commit data."""
        plt = self.plot_widget.plt
        plt.clear_figure()
        plt.theme("dark")

        # Set the plot size based on container size
        available_width = max(10, self.size.width - 2)  # Minimum width of 10
        available_height = max(10, self.size.height - 2)  # Minimum height of 10
        plt.plotsize(available_width, available_height)

        plt.title(self.title)
        plt.xlabel("Author")
        plt.ylabel("Number of Commits")

        if not self.data:
            return

        # Sort authors by commit count and take top 10
        sorted_data = sorted(self.data.items(), key=lambda x: x[1], reverse=True)[:10]
        authors = [item[0][:15] for item in sorted_data]  # Truncate long names
        counts = [item[1] for item in sorted_data]

        if authors:  # Only plot if we have data
            # Create vertical bar chart
            x_positions = [float(x) for x in range(len(authors))]

            # Plot the bars
            plt.bar(x_positions, counts, width=0.6)

            # Set x-axis labels (authors)
            plt.xticks(x_positions, authors)

        self.plot_widget.refresh()

    async def load_data(self, git_data) -> None:
        """Load author commit data."""
        self.is_loading = True
        try:
            self.data = git_data.get_commits_by_author()
        finally:
            self.is_loading = False

    def clear_data(self) -> None:
        """Clear the view's data."""
        self.data = {}
