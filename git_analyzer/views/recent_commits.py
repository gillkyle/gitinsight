"""View for displaying recent commits."""

from textual.reactive import reactive
from textual.widgets import DataTable

from .base import BaseView


class RecentCommitsView(BaseView):
    """A view to display recent commits in a table."""

    title = reactive("Recent Commits")
    data = reactive([])

    def __init__(self):
        super().__init__()
        self.table = DataTable()
        self.table.cursor_type = "row"

    def compose(self):
        """Compose the view with a data table."""
        yield self.table

    def on_mount(self) -> None:
        """Set up the table columns."""
        self.table.add_columns("Hash", "Author", "Date", "Message")
        self.refresh_table()

    def watch_data(self, value) -> None:
        """React to data changes."""
        self.refresh_table()

    def refresh_table(self) -> None:
        """Refresh the table with current data."""
        self.table.clear()
        for commit in self.data:
            self.table.add_row(
                commit.hash,
                commit.author,
                commit.date.strftime("%Y-%m-%d %H:%M"),
                commit.message,
            )

    async def load_data(self, git_data) -> None:
        """Load recent commits data."""
        self.is_loading = True
        self.data = git_data.get_recent_commits()
        self.is_loading = False

    def clear_data(self) -> None:
        """Clear the view's data."""
        self.data = []
