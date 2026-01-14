import datetime
import os
import shutil

from endstone import Logger
from .options import PluginOptions


class RetentionManager:
    def __init__(self, options: PluginOptions) -> None:
        self.options: PluginOptions = options
        self.logger: Logger | None = None

    def clean_backups(self, logger: Logger) -> None:
        retention = self.options.retention

        if not os.path.exists(self.options.output):
            return

        file_list = os.listdir(self.options.output)
        file_list = [f for f in file_list if f != ".tmp"]

        if not file_list:
            return

        # Build list of backups with their modification times
        backups: list[tuple[str, datetime.datetime]] = []
        for file_name in file_list:
            file_path = os.path.join(self.options.output, file_name)
            try:
                file_mtime = datetime.datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                )
                backups.append((file_name, file_mtime))
            except OSError:
                continue

        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x[1], reverse=True)

        now = datetime.datetime.now()
        to_keep: set[str] = set()

        # Strategy 1: Keep last N backups
        if retention.keep_last > 0:
            for file_name, _ in backups[: retention.keep_last]:
                to_keep.add(file_name)

        # Strategy 2: Keep backups for last X days
        if retention.keep_days > 0:
            cutoff = now - datetime.timedelta(days=retention.keep_days)
            for file_name, mtime in backups:
                if mtime >= cutoff:
                    to_keep.add(file_name)

        # Strategy 3: Keep hourly backups for X hours
        if retention.keep_hourly > 0:
            to_keep.update(
                self._get_periodic_backups(backups, now, retention.keep_hourly, "hour")
            )

        # Strategy 4: Keep daily backups for X days
        if retention.keep_daily > 0:
            to_keep.update(
                self._get_periodic_backups(backups, now, retention.keep_daily, "day")
            )

        # Strategy 5: Keep weekly backups for X weeks
        if retention.keep_weekly > 0:
            to_keep.update(
                self._get_periodic_backups(backups, now, retention.keep_weekly, "week")
            )

        # Strategy 6: Keep monthly backups for X months
        if retention.keep_monthly > 0:
            to_keep.update(
                self._get_periodic_backups(
                    backups, now, retention.keep_monthly, "month"
                )
            )

        # Delete backups not in the keep set
        for file_name, mtime in backups:
            if file_name not in to_keep:
                file_path = os.path.join(self.options.output, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"Deleted old backup: {file_name}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        logger.info(f"Deleted old backup: {file_name}")
                except OSError as e:
                    logger.error(f"Failed to delete backup {file_name}: {e}")

    def _get_periodic_backups(
        self,
        backups: list[tuple[str, datetime.datetime]],
        now: datetime.datetime,
        periods: int,
        period_type: str,
    ) -> set[str]:
        """
        Get the best backup for each time period.

        Args:
            backups: List of (filename, mtime) tuples sorted by mtime descending
            now: Current datetime
            periods: Number of periods to keep
            period_type: "hour", "day", "week", or "month"

        Returns:
            Set of filenames to keep
        """
        to_keep: set[str] = set()
        buckets: dict[str, tuple[str, datetime.datetime]] = {}

        for file_name, mtime in backups:
            key = self._get_period_key(mtime, now, periods, period_type)
            if key is None:
                continue

            # Keep the newest backup in each bucket
            if key not in buckets:
                buckets[key] = (file_name, mtime)
            elif mtime > buckets[key][1]:
                buckets[key] = (file_name, mtime)

        for file_name, _ in buckets.values():
            to_keep.add(file_name)

        return to_keep

    def _get_period_key(
        self,
        mtime: datetime.datetime,
        now: datetime.datetime,
        periods: int,
        period_type: str,
    ) -> str | None:
        """
        Get the bucket key for a backup based on its modification time.

        Returns None if the backup is outside the retention period.
        """
        if period_type == "hour":
            cutoff = now - datetime.timedelta(hours=periods)
            if mtime < cutoff:
                return None
            return mtime.strftime("%Y-%m-%d-%H")

        elif period_type == "day":
            cutoff = now - datetime.timedelta(days=periods)
            if mtime < cutoff:
                return None
            return mtime.strftime("%Y-%m-%d")

        elif period_type == "week":
            cutoff = now - datetime.timedelta(weeks=periods)
            if mtime < cutoff:
                return None
            return mtime.strftime("%Y-W%W")

        elif period_type == "month":
            cutoff_year = now.year
            cutoff_month = now.month - periods
            while cutoff_month <= 0:
                cutoff_month += 12
                cutoff_year -= 1
            cutoff = now.replace(year=cutoff_year, month=cutoff_month, day=1)
            if mtime < cutoff:
                return None
            return mtime.strftime("%Y-%m")

        return None
