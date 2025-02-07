#!/usr/bin/env python3
"""Main application module for Git Analyzer."""

import os

import click
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from .git_data import GitDataManager
from .views.author_commits import AuthorCommitsView
from .views.base import BaseView
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

    CSS = """
    StatusPanel {
        width: 100%;
        height: auto;
        background: $surface;
        color: $text;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    #navigation {
        width: 100%;
        height: auto;
        background: $surface;
        color: $text;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    Button {
        margin: 0 1;
    }

    Button:hover {
        background: $accent;
    }

    Button.selected {
        background: $accent;
    }

    #main-content {
        width: 100%;
        height: 1fr;
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
        self.current_view: BaseView | None = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Vertical(
                self.status_panel,
                Horizontal(
                    *[
                        Button(label, id=f"view-{key}", classes="nav-button")
                        for key, (_, label) in self.VIEWS.items()
                    ],
                    id="navigation",
                ),
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
            # Switch to the first view by default
            await self.switch_view("time")
        except ValueError as e:
            error_msg = str(e)
            self.status_panel.update_status(f"Error: {error_msg}")
            self.notify(error_msg, severity="error")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status_panel.update_status(error_msg)
            self.notify(error_msg, severity="error")

    async def switch_view(self, view_key: str) -> None:
        """Switch to a different view."""
        if view_key not in self.VIEWS:
            return

        # Clear the current view if it exists
        if self.current_view is not None:
            self.current_view.remove()

        # Create and mount the new view
        view_class, _ = self.VIEWS[view_key]
        new_view = view_class()
        new_view.add_class("view")
        self.current_view = new_view

        # Add the view to the main content area
        main_content = self.query_one("#main-content")
        main_content.mount(new_view)

        # Update button states
        for button in self.query(".nav-button"):
            button.remove_class("selected")
        self.query_one(f"#view-{view_key}").add_class("selected")

        # Load data for the new view
        try:
            self.status_panel.update_status("Loading data...")
            await new_view.load_data(self.git_data)
            self.status_panel.update_status("Data loaded successfully!")
        except ValueError as e:
            error_msg = str(e)
            self.status_panel.update_status(f"Error: {error_msg}")
            self.notify(error_msg, severity="error")
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.status_panel.update_status(error_msg)
            self.notify(error_msg, severity="error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id and event.button.id.startswith("view-"):
            view_key = event.button.id.replace("view-", "")
            await self.switch_view(view_key)


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
