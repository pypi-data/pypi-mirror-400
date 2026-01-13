import importlib

from todotree.Commands.AbstractCommand import AbstractCommand


class Version(AbstractCommand):

    def run(self):
        from importlib.metadata import version
        version_number = version("todotree")
        if self.config.console.is_verbose():
            self.config.console.verbose(f"The version is {version_number}")
        elif self.config.console.is_quiet():
            self.config.console.warning(version_number)
        else:
            self.config.console.info(f"Version: {version_number}")

    def __call__(self, *args, **kwargs):
        NotImplemented