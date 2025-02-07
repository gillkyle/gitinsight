#!/usr/bin/env python3
"""Main application module for Git Analyzer."""

import os

import click
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Static, Tab, Tabs

from .git_data import GitDataManager
from .views.author_commits import AuthorCommitsView
from .views.commit_time import CommitTimeView
from .views.recent_commits import RecentCommitsView


class StatusPanel(Static):
    """Shows repository and status information."""

    def __init__(self):
        super().__init__()
        self.repo_info = Static("Repository: Not connected")
        self.status = Static("Status: Initializing...")

    def compose(self) -> ComposeResult:
        yield self.repo_info
        yield self.status

    def update_repo_info(self, path: str) -> None:
        self.repo_info.update(f"Repository: {os.path.abspath(path)}")

    def update_status(self, message: str) -> None:
        self.status.update(f"Status: {message}")


class GitAnalyzerApp(App):
    """Main application for analyzing git repositories."""

    BINDINGS = [
        Binding("left", "previous_tab", "Previous tab", show=True, key_display="←"),
        Binding("right", "next_tab", "Next tab", show=True, key_display="→"),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    StatusPanel {
        width: 100%;
        height: auto;
        background: $primary;
        color: $text;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    Tabs {
        width: 100%;
        height: 3;  /* Fixed height for tabs */
        background: $boost;
        border-bottom: solid $primary;
    }

    Tabs > .tab-list {
        height: 100%;
        background: $boost;
        color: $text;
    }

    Tabs > .tab-list > Tab {
        margin: 0 1;
        padding: 0 2;
        height: 100%;
        text-style: bold;
        background: $panel;
        color: $text;
        border: tall $primary;
    }

    Tab:hover {
        background: $accent-darken-1;
    }

    Tab.-active {
        background: $accent;
        color: $text;
        text-style: bold;
        border-bottom: none;
    }

    Footer {
        background: $boost;
        color: $text;
        padding: 0 1;
    }

    Footer > .footer--key {
        text-style: bold;
        background: $primary;
        color: $text;
    }

    Footer > .footer--highlight {
        background: $primary;
        color: $text;
    }

    #main-content {
        width: 100%;
        height: 100%;
        layout: grid;
        grid-size: 1;
        grid-rows: auto auto 1fr;  /* Status panel, tabs, and content */
    }

    #tab-content {
        width: 100%;
        height: 100%;
    }

    .view {
        width: 100%;
        height: 100%;
        background: $surface;
        color: $text;
        border: solid $primary;
        padding: 1;
    }
    """

    VIEWS = {
        "time": (CommitTimeView, "Commits by Time"),
        "authors": (AuthorCommitsView, "Commits by Author"),
        "recent": (RecentCommitsView, "Recent Commits"),
    }

    def __init__(self, repo_path: str):
        super().__init__()
        self.repo_path = repo_path
        self.git_data = GitDataManager(repo_path)
        self.status_panel = StatusPanel()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Vertical(
                self.status_panel,
                Tabs(
                    *[Tab(label, id=key) for key, (_, label) in self.VIEWS.items()],
                    id="tabs",
                ),
                Container(id="tab-content"),
                id="main-content",
            )
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Handle app mount event."""
        self.status_panel.update_repo_info(self.repo_path)
        try:
            self.status_panel.update_status("Connecting to repository...")
            self.git_data.connect()
            self.status_panel.update_status("Connected successfully!")

            # Create and mount the first view
            first_key = next(iter(self.VIEWS.keys()))
            await self._show_view(first_key)

            self.status_panel.update_status("View loaded successfully!")
        except ValueError as e:
            error_msg = str(e)
            self.status_panel.update_status(f"Error: {error_msg}")
            self.notify(error_msg, severity="error")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status_panel.update_status(error_msg)
            self.notify(error_msg, severity="error")

    async def _show_view(self, key: str) -> None:
        """Show the view for the given key."""
        if key not in self.VIEWS:
            return

        # Clear current content
        content_container = self.query_one("#tab-content")
        content_container.remove_children()

        # Create and mount new view
        view_class, _ = self.VIEWS[key]
        view = view_class()
        view.add_class("view")
        content_container.mount(view)
        await view.load_data(self.git_data)

    async def on_tabs_tab_activated(self, event) -> None:
        """Handle tab activation events."""
        tab_id = event.tab.id
        if tab_id:
            await self._show_view(tab_id)
            self.status_panel.update_status(f"Viewing {event.tab.label}")

    async def action_previous_tab(self) -> None:
        """Switch to the previous tab."""
        tabs = self.query_one(Tabs)
        tabs.action_previous_tab()

    async def action_next_tab(self) -> None:
        """Switch to the next tab."""
        tabs = self.query_one(Tabs)
        tabs.action_next_tab()


@click.command()
@click.argument("repo_path", type=click.Path(exists=True))
def main(repo_path: str):
    """Analyze git repository commit patterns."""
    if not os.path.exists(os.path.join(repo_path, ".git")):
        click.echo("Error: Not a git repository")
        return

    app = GitAnalyzerApp(repo_path)
    app.run()


if __name__ == "__main__":
    main()
