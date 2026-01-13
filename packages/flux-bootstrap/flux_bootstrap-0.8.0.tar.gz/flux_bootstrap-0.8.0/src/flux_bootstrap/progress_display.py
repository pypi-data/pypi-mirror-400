"""Rich progress display components for CLI."""

from rich.console import Console, Group
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from flux_bootstrap.data_structures import MAX_UNVERIFIED_PARTS


class MbpsColumn(ProgressColumn):
    """Custom column to show speed in Mbps with fixed width."""

    def render(self, task):
        """Render speed in Mbps format."""
        # Use custom mbps field if available (explicitly set by us)
        # Otherwise fall back to Rich's auto-calculated speed
        if hasattr(task, "fields") and "mbps" in task.fields:
            mbps = task.fields["mbps"]
            if mbps is not None:
                return Text(f"{mbps:5.1f} Mbps", style="progress.data.speed")

        if task.speed is None:
            return Text("   -- Mbps", style="progress.data.speed")

        # Convert bytes/sec to Mbps (megabits per second)
        # 1 byte = 8 bits, 1 MB = 1024*1024 bytes
        mbps = (task.speed * 8) / (1024 * 1024)
        return Text(f"{mbps:5.1f} Mbps", style="progress.data.speed")


class CustomFileSizeColumn(ProgressColumn):
    """Custom file size column that handles large numbers correctly with fixed width."""

    def render(self, task):
        """Render file size with appropriate units."""

        def format_size(size):
            if size == 0:
                return "    0 bytes"
            elif size < 1024:
                return f"{size:4.0f} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:6.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):6.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):6.1f} GB"

        completed = format_size(task.completed)
        total = format_size(task.total or 0)

        return Text(f"{completed} of {total}", style="progress.filesize")


class ProgressDisplay:
    """Rich progress display for CLI with multiple progress bars and status table."""

    def __init__(self, console: Console, total_bytes: int, total_parts: int):
        """Initialize progress display.

        Args:
            console: Rich console instance
            total_bytes: Total bytes to download
            total_parts: Total number of parts
        """
        self.console = console
        self.total_bytes = total_bytes
        self.total_parts = total_parts

        # Progress instance with custom columns
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            CustomFileSizeColumn(),
            MbpsColumn(),
            TimeRemainingColumn(),
            console=console,
            expand=True,
        )

        # Task tracking
        self.overall_task_id = None
        self.part_tasks = {}  # part_id -> task_id

        # Statistics for status table
        self.parts_completed = 0
        self.current_speed = 0.0
        self.current_cdn = None
        self.verification_slots_used = 0
        self.is_extracting = False

    def start(self):
        """Start the progress display by creating the overall task."""
        self.overall_task_id = self.progress.add_task(
            "Overall Progress", total=self.total_bytes, completed=0
        )

    def update_from_callback(self, progress_data: dict):
        """Update progress from download manager callback.

        Args:
            progress_data: Progress data dict with:
                - bytes_downloaded: Total bytes downloaded
                - total_bytes: Total expected bytes
                - speed_mbps: Current speed in Mbps
                - cdn_server: Current CDN server hostname
                - current_part: Current part number (1-indexed)
                - total_parts: Total number of parts
                - part_bytes_downloaded: Bytes downloaded for current part
                - part_total_bytes: Total bytes for current part
        """
        # Update overall progress
        if self.overall_task_id is not None:
            self.progress.update(
                self.overall_task_id,
                completed=progress_data["bytes_downloaded"],
                mbps=progress_data.get("speed_mbps"),  # Explicit overall speed
            )

        # Create or update part task
        part_id = progress_data["current_part"] - 1  # Convert to 0-indexed
        part_bytes = progress_data.get("part_bytes_downloaded", 0)
        part_total = progress_data.get("part_total_bytes", 0)
        part_speed = progress_data.get("part_speed_mbps", 0)

        if part_id not in self.part_tasks and part_total > 0:
            # Create new part task
            task_id = self.progress.add_task(
                f"Part {progress_data['current_part']}/{progress_data['total_parts']}",
                total=part_total,
                completed=part_bytes,
                visible=True,
                mbps=part_speed,  # Explicit part speed
            )
            self.part_tasks[part_id] = task_id
        elif part_id in self.part_tasks:
            # Update existing part task
            self.progress.update(
                self.part_tasks[part_id],
                completed=part_bytes,
                mbps=part_speed,  # Explicit part speed
            )

        # Update statistics
        self.current_speed = progress_data.get("speed_mbps", 0.0)
        self.current_cdn = progress_data.get("cdn_server")

    def mark_part_complete(self, part_id: int):
        """Remove completed part progress bar and update stats.

        Args:
            part_id: Part number (0-indexed)
        """
        if part_id in self.part_tasks:
            task_id = self.part_tasks.pop(part_id)
            self.progress.remove_task(task_id)
            self.parts_completed += 1

    def update_verification_slots(self, used: int, total: int):
        """Update verification buffer statistics.

        Args:
            used: Number of slots currently used
            total: Total number of slots available (kept for API compatibility)
        """
        self.verification_slots_used = used
        _ = total  # Unused but kept for API compatibility

    def show_extraction_status(self):
        """Mark that extraction has started."""
        self.is_extracting = True

    def get_status_table(self) -> Table:
        """Create status summary table.

        Returns:
            Rich Table with current status information
        """
        table = Table.grid(padding=(0, 2))

        # Row 1: Currently downloading parts
        downloading = [f"Part {pid + 1}" for pid in self.part_tasks]
        if downloading and not self.is_extracting:
            table.add_row(
                f"[cyan]Downloading:[/cyan] {', '.join(downloading)}",
                "",
            )
        elif self.is_extracting:
            table.add_row(
                "[cyan]Status:[/cyan] Extracting...",
                "",
            )

        # Row 2: CDN and verification buffer
        if self.current_cdn:
            table.add_row(
                f"[cyan]CDN:[/cyan] {self.current_cdn}",
                f"[cyan]Verify Buffer:[/cyan] "
                f"{self.verification_slots_used}/{MAX_UNVERIFIED_PARTS}",
            )

        return table

    def get_renderable(self):
        """Get renderable for Live display.

        Returns:
            Rich Group containing progress and status table
        """
        return Group(
            self.progress,
            Text(""),  # Blank line
            self.get_status_table(),
        )
