import click

from todotree.Config.AbstractSubConfig import AbstractSubConfig


class ConsolePrefixes(AbstractSubConfig):
    """Class for handling the prefixes in the terminal.

    The class is somewhat similar to a simple logger. It prints messages with a configured prefix.
    """

    def __init__(self, enable_colors: bool,
                 info_prefix: str, warning_prefix: str, error_prefix: str,
                 info_color: str, warn_color: str, error_color: str):
        """
        Initialize a new Console Prefix.
        :param enable_colors: Whether to enable colors.
        :param info_prefix: The prefix for information messages.
        :param warning_prefix: The prefix for warning messages.
        :param error_prefix: The prefix for error messages.
        """
        self.enable_colors = enable_colors
        self.error_prefix = error_prefix
        self.warning_prefix = warning_prefix
        self.info_prefix = info_prefix
        self.info_color = info_color
        self.warn_color = warn_color
        self.error_color = error_color

        self.__detail = 0
        """An integer indicating how much detail is printed."""

    def verbose(self, message):
        """
        Print an info message if verbose is turned on.
        """
        if self.__detail > 0:
            self.info(message)

    def info(self, message):
        """
        Print an information message to console if quiet is not on.
        :param message: The message to print.
        """
        if self.__detail >= 0:
            self.__emit(self.info_prefix, self.info_color, message)

    def warning(self, message: str):
        """
        Print a warning message to the console.
        :param message: The message to print.
        """
        self.__emit(self.warning_prefix, self.warn_color, message)

    def error(self, message: str):
        """
        Print an error message to the console.
        :param message: The message to print.
        """
        self.__emit(self.error_prefix, self.error_color, message)

    def __emit(self, prefix: str, color: str, message: str):
        """
        Print a message with a prefix.
        :param prefix: The prefix of the message.
        :param message: The message itself.
        """
        # Emit the prefix.
        self._emit_prefix(color, prefix)
        # Emit the message.
        click.echo(message)

    def _emit_prefix(self, color, prefix):
        """Print the prefix with color if enabled."""
        if self.enable_colors:
            click.secho(prefix, fg=color, nl=False)
        else:
            click.echo(prefix, nl=False)

    def is_verbose(self):
        return self.__detail > 0

    def set_verbose(self):
        """Turns on verbose messaging."""
        self.__detail = 1

    def set_quiet(self):
        """Disables info messages."""
        self.__detail = -1

    def is_quiet(self):
        """Return whether quiet is turned on."""
        return self.__detail < 0

    def read_from_dict(self, new_values: dict):
        self.enable_colors = new_values.get('enable_colors', self.enable_colors)
        self.info_prefix = new_values.get('info', self.info_prefix)
        self.warning_prefix = new_values.get('warning', self.warning_prefix)
        self.error_prefix = new_values.get('error', self.error_prefix)
        self.info_color = new_values.get('info_color', self.info_color)
        self.warn_color = new_values.get('warning_color', self.warn_color)
        self.error_color = new_values.get('error_color', self.error_color)

    def apply_to_dict(self, dict_to_modify: dict):
        dict_to_modify['enable_colors'] = self.enable_colors
        dict_to_modify['info'] = self.info_prefix
        dict_to_modify['warning'] = self.warning_prefix
        dict_to_modify['error'] = self.error_prefix
        dict_to_modify['info_color'] = self.info_color
        dict_to_modify['warning_color'] = self.warn_color
        dict_to_modify['error_color'] = self.error_color

    def __repr__(self):
        return f"ConsolePrefixes({', '.join([str(x) for x in list(self.__dict__.values())])})"
