from typing import override

from todotree.Errors.TodotreeError import TodotreeError


class RecurDateStampError(TodotreeError):
    """
    Represents an error when parsing the recur date stamp.
    """

    @override
    def echo_and_exit(self, config: 'Config', malformeddate: str):
        config.console.error(f"The date in the timestamp file is malformed {malformeddate}")
        config.console.error("You can repair this by adding the --date {date} option to recur.")
        config.console.verbose(str(self))
        exit(1)
