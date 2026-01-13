import click

from todotree.Config.ConsolePrefixes import ConsolePrefixes


class ConsolePrefixesInit(ConsolePrefixes):
    """
    Provides additional features to ConsolePrefixes.
    These are only used in the Init command.
    """
    def __init__(self, enable_colors: bool,
                 info_prefix: str, warning_prefix: str, error_prefix: str,
                 info_color: str, warn_color: str, error_color: str):
        super().__init__(enable_colors,
                         info_prefix, warning_prefix, error_prefix,
                         info_color, warn_color, error_color)
        self.enable_colors = enable_colors
        self.error_prefix = error_prefix
        self.warning_prefix = warning_prefix
        self.info_prefix = info_prefix
        self.info_color = info_color
        self.warn_color = warn_color
        self.error_color = error_color

    @staticmethod
    def from_console_prefixes(c: ConsolePrefixes):
        """Converts from console prefixes."""
        return ConsolePrefixesInit(
            enable_colors=c.enable_colors,
            info_prefix=c.info_prefix,
            warning_prefix=c.warning_prefix,
            error_prefix=c.error_prefix,
            info_color=c.info_color,
            warn_color=c.warn_color,
            error_color=c.error_color
        )

    def prompt_menu(self, question: str, answers: list, custom_answer: str | None = None) -> str | int:
        """
        Ask the end user for input using a menu.
        @param question: The question to ask the user.
        @param answers: The predefined answers that the user can select.
        @param custom_answer: The custom option Text. Do not append with a dot.
            If the user chooses the Custom answer option. The user will be prompted to fill in the custom answer.
        @return: The answer that the user chose.
        If the user chooses a predefined option, it will be number of that option.
        It will be a string if the answer came from the custom option.
        """
        confirmed = False
        while not confirmed:
            text = question
            click.echo(text)
            for i, answer in enumerate(answers):
                self._menu_line(i, answer)
            custom_answer_number = len(answers)
            if custom_answer:
                self._menu_line(custom_answer_number, custom_answer)

            choices = [str(i) for i in range(0, custom_answer_number + 1)]
            answer_int = int(self.prompt(text='', show_choices=False, type=click.Choice(choices),
                                         prompt_suffix="Your answer:"))
            if custom_answer and answer_int == custom_answer_number:
                answer = self.prompt(text=f"{custom_answer} option chosen. Please type it in.")
                confirmed = self.confirm(text=f"Is this correct?: {answer}")
            else:
                answer = answer_int
                confirmed = self.confirm(text=f"Is this correct?: {answers[answer_int]}")
        return answer

    def _menu_line(self, answer_number: int, answer: str):
        """Prints a menu line (with colors if enabled."""
        if self.enable_colors:
            click.secho(f"  [{str(answer_number)}] ", fg=self.info_color, nl=False)
        else:
            click.echo(f"  [{str(answer_number)}] ", nl=False)
        click.echo(answer)

    def prompt(self, *args, **kwargs):
        """Wrapper for click.prompt"""
        self._emit_prefix(self.warn_color, self.warning_prefix)
        return click.prompt(*args, **kwargs)

    def confirm(self, *args, **kwargs):
        """Wrapper for click.confirm"""
        self._emit_prefix(self.warn_color, self.warning_prefix)
        return click.confirm(*args, **kwargs)
