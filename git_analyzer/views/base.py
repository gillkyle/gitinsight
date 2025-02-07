"""Base view class for GitInsight views."""

from textual.reactive import reactive
from textual.widgets import Static


class BaseView(Static):
    """Base class for all views in GitInsight."""

    title = reactive("Unnamed View")
    is_loading = reactive(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loading_indicator = Static("Loading...", classes="loading-indicator")
        self.loading_indicator.display = False

    def watch_is_loading(self, value: bool) -> None:
        """React to loading state changes."""
        self.loading_indicator.display = value

    async def load_data(self) -> None:
        """Load data for the view. Should be implemented by subclasses."""
        raise NotImplementedError

    def clear_data(self) -> None:
        """Clear the view's data. Should be implemented by subclasses."""
        raise NotImplementedError
