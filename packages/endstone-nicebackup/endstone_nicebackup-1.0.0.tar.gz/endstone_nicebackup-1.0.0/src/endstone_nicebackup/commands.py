from endstone import Logger, Server
from endstone.lang import Translatable
from endstone.command import CommandSender, CommandSenderWrapper


class CommandMessages:
    def __init__(self, text: str, params: list[str]) -> None:
        self.text: str = text
        self.params: list[str] = params


class CommandResult:
    def __init__(self, command_line: str) -> None:
        self.has_error: bool = False
        self.messages: list[CommandMessages] = []
        self.errors: list[CommandMessages] = []
        self.command_line: str = command_line

    def add_message(self, msg: str | Translatable) -> None:
        text = msg if isinstance(msg, str) else msg.text
        params = [] if isinstance(msg, str) else msg.params
        self.messages.append(CommandMessages(text, params))

    def add_error(self, msg: str | Translatable) -> None:
        text = msg if isinstance(msg, str) else msg.text
        params = [] if isinstance(msg, str) else msg.params
        self.errors.append(CommandMessages(text, params))

    def log_messages(self, logger: Logger) -> None:
        self._log_items(self.messages, logger.info)

    def log_errors(self, logger: Logger) -> None:
        self._log_items(self.errors, logger.error)

    def _log_items(self, items: list[CommandMessages], log_fn) -> None:
        for i, item in enumerate(items):
            log_fn(f"[{i}] - {item.text}")
            for j, param in enumerate(item.params):
                log_fn(f"[{i}.{j}]   - Param: {param}")


class CommandBuilder:
    def __init__(self, sender: CommandSender, command_line: str) -> None:
        self.sender: CommandSender = sender
        self.server: Server = sender.server
        self.command_line: str = command_line
        self.response: bool = False
        self.result: CommandResult = CommandResult(command_line)

    def execute(self) -> CommandResult:
        def on_message(msg: Translatable | str) -> None:
            self.result.add_message(msg)

        def on_error(msg: Translatable | str) -> None:
            self.result.has_error = True
            self.result.add_error(msg)

        sender = CommandSenderWrapper(
            self.server.command_sender,
            on_message=on_message,
            on_error=on_error,
        )

        self.response = self.server.dispatch_command(sender, self.command_line)
        return self.result
