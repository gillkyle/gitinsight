#!/usr/bin/env python3
import os
from collections import defaultdict

import click
import git
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, Static
from textual_plotext import PlotextPlot


class StatusPanel(Static):
    """Shows repository and command status information."""

    def __init__(self):
        super().__init__()
        self.repo_info = Label("Repository: Not connected")
        self.status = Label("Status: Initializing...")
        self.command = Label("Command: None")

    def compose(self) -> ComposeResult:
        yield self.repo_info
        yield self.status
        yield self.command

    def update_repo_info(self, path: str) -> None:
        self.repo_info.update(f"Repository: {os.path.abspath(path)}")

    def update_status(self, message: str) -> None:
        self.status.update(f"Status: {message}")

    def update_command(self, command: str) -> None:
        self.command.update(f"Command: {command}")


class CommitTimeChart(PlotextPlot):
    """A widget to display commit time distribution using textual-plotext."""

    data = reactive(defaultdict(int))

    def watch_data(self, value) -> None:
        """React to data changes."""
        self.refresh_chart()

    def refresh_chart(self) -> None:
        self.plot()

    def on_mount(self) -> None:
        self.refresh_chart()

    def plot(self) -> None:
        if not self.data:
            return

        self.plt.clear_figure()
        self.plt.theme("dark")

        hours = list(range(24))
        counts = [self.data[hour] for hour in hours]

        if any(counts):  # Only plot if we have data
            self.plt.bar(hours, counts, width=0.8)
            self.plt.title("Commits by Hour of Day")
            self.plt.xlabel("Hour (24h format)")
            self.plt.ylabel("Number of Commits")

            # Add value labels on top of bars
            for hour, count in enumerate(counts):
                if count > 0:
                    # Position the text slightly above each bar
                    self.plt.text(str(count), float(hour), float(count) + 0.5)


class GitInsightApp(App):
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

    CommitTimeChart {
        width: 100%;
        height: 1fr;
        background: $surface;
        color: $text;
        border: solid $primary;
        padding: 1;
    }

    Label {
        padding: 0 1;
        height: 1;
    }
    """

    def __init__(self, repo_path: str):
        super().__init__()
        self.repo_path = repo_path
        self.status_panel = StatusPanel()
        self.chart = CommitTimeChart()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(Vertical(self.status_panel, self.chart))
        yield Footer()

    def on_mount(self) -> None:
        self.status_panel.update_repo_info(self.repo_path)
        self.analyze_commits()

    def analyze_commits(self) -> None:
        try:
            self.status_panel.update_status("Connecting to repository...")
            repo = git.Repo(self.repo_path)

            # Show the equivalent git command
            git_command = "git log --format='%aI' | awk '{print substr($1,12,2)}' | sort -n | uniq -c"
            self.status_panel.update_command(git_command)

            self.status_panel.update_status("Analyzing commits...")
            commit_times = defaultdict(int)
            commit_count = 0

            for commit in repo.iter_commits():
                hour = commit.authored_datetime.hour
                commit_times[hour] += 1
                commit_count += 1
                if commit_count % 100 == 0:
                    self.status_panel.update_status(
                        f"Processing commits... (analyzed {commit_count} commits)"
                    )

            self.chart.data = commit_times
            self.status_panel.update_status(
                f"Analysis complete! Found {commit_count} commits"
            )

        except git.InvalidGitRepositoryError:
            error_msg = "Error: Invalid git repository"
            self.status_panel.update_status(error_msg)
            self.notify(error_msg, severity="error")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.status_panel.update_status(error_msg)
            self.notify(error_msg, severity="error")


@click.command()
@click.argument("repo_path", type=click.Path(exists=True))
def main(repo_path: str):
    """Analyze git repository commit patterns."""
    if not os.path.exists(os.path.join(repo_path, ".git")):
        click.echo("Error: Not a git repository")
        return

    app = GitInsightApp(repo_path)
    app.run()


if __name__ == "__main__":
    main()
