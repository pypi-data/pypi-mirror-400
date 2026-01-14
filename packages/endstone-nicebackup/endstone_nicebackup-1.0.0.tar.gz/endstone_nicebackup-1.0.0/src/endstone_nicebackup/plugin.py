import datetime
import os
import re
import shutil

from enum import Enum

from croniter import croniter

from endstone import Server
from endstone.scheduler import Task
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender

from .utilities import copy_backup, del_folder
from .options import PluginOptions
from .retention import RetentionManager
from .commands import CommandBuilder, CommandResult


class QueryStatus(Enum):
    COMPLETE = 1
    RUNNING = 2
    ERROR = 3


class NiceBackup(Plugin):
    prefix = "NiceBackup"
    api_version = "0.6"
    load = "POSTWORLD"

    description = "A simple backup scheduler plugin for Endstone."
    authors = ["Kapdap <kapdap@pm.me>"]
    website = "https://github.com/kapdap/endstone-nicebackup"

    commands = {
        "nice_backup": {
            "description": "Create a backup of the current world.",
            "usages": ["/nice_backup"],
            "permissions": ["nice_backup.command.backup"],
        }
    }

    permissions = {
        "nice_backup.command": {
            "description": "Allow use of /nice_backup command.",
            "default": "op",
        }
    }

    def __init__(self) -> None:
        self.options = PluginOptions()
        self.next_backup: datetime.datetime | None = None
        self.file_sizes: dict[str, int] = {}
        self.tasks: dict[str, Task] = {}
        self.retention: RetentionManager = RetentionManager(self.options)
        self.is_ready: bool = False
        return super().__init__()

    def read_config(self) -> None:
        self.save_default_config()

        self.options.load(self.config)
        self.logger.debug(f"Config loaded: {self.options.dump()}")

        self.level_name: str = self.get_level_name()
        self.world_path: str = self.options.worlds_path + "/" + self.level_name

    def on_enable(self) -> None:
        try:
            self.read_config()
            self.is_ready: bool = True

            self.logger.info(f"World path: {self.world_path}")
            self.logger.info(f"Backup path: {self.options.output}")
            self.logger.info(f"Backup schedule: {self.options.schedule or 'disabled'}")
            self.logger.info(
                f"Compression: {'enabled' if self.options.compress else 'disabled'}"
            )
        except Exception as e:
            self.is_ready: bool = False
            self.logger.error(f"Failed to enable plugin: {e}")

        if self.is_ready and self.options.schedule != "":
            self.start_schedule()

    def on_disable(self) -> None:
        self.stop_schedule()

    def on_command(
        self, sender: CommandSender, command: Command, args: list[str]
    ) -> bool:
        if command.name == "nice_backup":
            return self.create_backup(sender)

        return False

    def start_schedule(self) -> None:
        if self.options.schedule == "":
            self.logger.error("Backup schedule is disabled.")

        try:
            croniter(self.options.schedule, datetime.datetime.now())
        except (KeyError, ValueError) as e:
            self.logger.error(
                f"Invalid cron expression in schedule '{self.options.schedule}': {e}"
            )
            return

        self.update_next_backup()

        def schedule_backup_task() -> None:
            if self.next_backup and datetime.datetime.now() >= self.next_backup:
                self.create_backup(self.server.command_sender)
                self.update_next_backup()
                self.logger.info(
                    f"Next backup scheduled: {self.next_backup.strftime('%Y-%m-%d %H:%M:%S')}"
                )

        self.run_task("schedule", schedule_backup_task, 0, int(self.server.current_tps))

    def stop_schedule(self) -> None:
        self.logger.info("Stopping scheduled backups...")
        self.cancel_task("schedule")

    def update_next_backup(self) -> None:
        if self.options.schedule != "":
            cron = croniter(self.options.schedule, datetime.datetime.now())
            self.next_backup = cron.get_next(datetime.datetime)

    def create_backup(self, sender: CommandSender) -> bool:
        self.logger.info("Creating world backup...")

        server = sender.server

        result = self.execute_command(server.command_sender, "save hold")

        if result.has_error:
            if "commands.generic.running" in result.errors[0].text:
                self.logger.error(
                    "A backup is already in progress. Aborting new backup."
                )
            else:
                self.logger.error(f"Failed to execute command: {result.command_line}")
                result.log_errors(self.logger)
            return False

        self.clear_file_sizes()

        timeout = datetime.datetime.now() + datetime.timedelta(
            seconds=self.options.timeout
        )

        def get_status_task() -> None:
            try:
                if self.get_status(server) == QueryStatus.COMPLETE:
                    self.cancel_task("get_status")

                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_name = self.options.filename.format(
                        level_name=self.level_name, timestamp=timestamp
                    )

                    output_path = self.options.output + "/" + file_name
                    output_path_tmp = self.options.output_tmp + "/" + file_name

                    copy_backup(self.world_path, output_path_tmp, self.file_sizes)

                    self.save_resume(server)
                    self.save_backup(output_path_tmp, output_path)

                    del_folder(self.options.output_tmp)

                    self.retention.clean_backups(self.logger)
                elif datetime.datetime.now() > timeout:
                    raise Exception(
                        f"Failed to complete backup within the timeout period ({self.options.timeout} seconds)."
                    )
            except Exception as e:
                self.logger.error(str(e))
                
                self.cancel_task("get_status")
                self.save_resume(server)
                
                del_folder(self.options.output_tmp)

        self.run_task(
            "get_status",
            get_status_task,
            int(self.server.current_tps),
            int(self.server.current_tps),
        )

        return True

    def get_status(self, server: Server) -> QueryStatus:
        result = self.execute_command(server.command_sender, "save query")

        if result.has_error:
            if "commands.save-on.notDone" in result.errors[0].text:
                self.logger.info("Backup is still running...")
                return QueryStatus.RUNNING
            else:
                self.logger.error(f"Failed to execute command: {result.command_line}")
            result.log_errors(self.logger)
            return QueryStatus.ERROR

        if "commands.save-all.success" in result.messages[0].text:
            self.set_file_sizes(result.messages[1].params[0].split(", "))
            return QueryStatus.COMPLETE

        return QueryStatus.RUNNING

    def save_resume(self, server: Server) -> None:
        result = self.execute_command(server.command_sender, "save resume")

        if result.has_error:
            self.logger.error(f"Failed to execute command: {result.command_line}")
            result.log_errors(self.logger)

    def set_file_sizes(self, list: list[str]) -> None:
        for info in list:
            parts = info.split(":")
            if len(parts) == 2:
                self.file_sizes[parts[0]] = int(parts[1])

    def clear_file_sizes(self) -> None:
        self.file_sizes = {}

    def save_backup(self, path_tmp: str, path: str) -> None:
        message = f"Backup saved to: {path}"

        if self.options.compress:
            shutil.make_archive(path, "zip", path_tmp)
            os.rename(path + ".zip", path + self.options.extension)
            message += self.options.extension
        else:
            shutil.move(path_tmp, path)

        self.logger.info(message)

    def get_level_name(self) -> str:
        with open("./server.properties", "r") as file:
            buffer = file.read()

            match = re.search(r"^level-name=(.*)$", buffer, re.MULTILINE)
            if not match:
                raise Exception("Could not find level-name in server.properties")

            return match.group(1)

    def execute_command(
        self, sender: CommandSender, command_line: str
    ) -> CommandResult:
        command = CommandBuilder(
            sender,
            command_line,
        )
        self.logger.debug(f"Executing command: {command.command_line}")
        result = command.execute()
        return result

    def run_task(self, name: str, task, delay: int, period: int) -> Task:
        if name in self.tasks:
            raise Exception(f"Task with name '{name}' already exists.")

        self.tasks[name] = self.server.scheduler.run_task(self, task, delay, period)

        return self.tasks[name]

    def cancel_task(self, task_name: str) -> None:
        if task_name in self.tasks:
            self.tasks[task_name].cancel()
            del self.tasks[task_name]
