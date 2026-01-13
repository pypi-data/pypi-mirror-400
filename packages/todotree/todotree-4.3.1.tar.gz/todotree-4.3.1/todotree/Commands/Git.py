from todotree.Commands.AbstractCommand import AbstractCommand
import click


class Git(AbstractCommand):

    def run(self, command: str) -> None:
        stdout, stderr = self.__call__(command)
        click.echo(stdout)
        if stderr:
            click.secho(stderr, fg='red')

    def __call__(self, command: str):
        return self.config.git.run_raw_command(command=command)
