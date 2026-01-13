from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from git import Repo, InvalidGitRepositoryError, NoSuchPathError, GitCommandError, FetchInfo, Git
from git.util import IterableList

from todotree.Config.AbstractSubConfig import AbstractSubConfig
from todotree.Config.ConsolePrefixes import ConsolePrefixes
from todotree.Errors.GitError import GitError

import subprocess
import click

class GitHandler(AbstractSubConfig):
    """
    Handles all git related functionality.
    """

    class GitModeEnum(Enum):
        disabled = 0
        """Git functionality is disabled."""
        local = 1
        """Add and commits automatically"""
        full = 2
        """Also pulls and pushes to a remote repo"""

    def __init__(self, new_git_mode: str, pull_time_minutes: int, todo_folder: Path, console: ConsolePrefixes):
        self.todo_folder = todo_folder
        self.console = console
        self.pull_time_minutes = pull_time_minutes
        self.git_mode = new_git_mode

    @property
    def git_mode(self):
        return self.__git_mode

    @git_mode.setter
    def git_mode(self, new_mode):
        try:
            self.__git_mode: GitHandler.GitModeEnum = GitHandler.GitModeEnum[new_mode.lower()]
        except KeyError:
            self.console.warning(f"The git mode '{new_mode}' is not valid.")
            self.console.warning("The options are " + str([x.name for x in self.GitModeEnum]))
            self.console.warning("Continuing with the mode 'disabled'.")
            self.__git_mode = GitHandler.GitModeEnum.disabled
        if self.__git_mode is not GitHandler.GitModeEnum.disabled:
            try:
                self.repo: Repo = Repo(self.todo_folder)
            except InvalidGitRepositoryError:
                self.console.error("Git repository is not initialized.")
                self.console.error(f"Run `git init -C {self.todo_folder}` to initialize the repository.")
                self.console.error("Or disable the git functionality by setting git.mode to disabled in config.yaml")
                raise GitError("Git repository is not Initialized.")
            except NoSuchPathError:
                self.console.error("Directory is not found.")

    def git_pull(self):
        """
        Runs `git pull` on the TodoTree folder.

        - Does not pull if the previous pull time recent.
        - Only pulls if git_mode = Full
        """
        if self.__git_mode != GitHandler.GitModeEnum.full:
            return
        # Check last pull time.
        # Repo does not have a function to access FETCH_HEAD,
        # So this is done manually.
        fetch_head = Path(self.repo.git_dir) / "FETCH_HEAD"

        if fetch_head.exists():
            # Then the repo has been pulled once in its lifetime.
            if (datetime.now() - datetime.fromtimestamp(fetch_head.stat().st_mtime) <
                    timedelta(minutes=self.pull_time_minutes)):
                # Then the repo is pulled fairly recently. Do not do anything.
                self.console.verbose(
                    f"Repo was pulled recently at {datetime.fromtimestamp(fetch_head.stat().st_mtime)}. Not pulling.")
                return
        else:
            self.console.info("Pulling git repo for the first time.")

        # Pull the repo
        self.console.info("Pulling latest changes.")
        try:
            Repo(self.todo_folder).remote()
        except ValueError as e:
            self.console.error("Error Pulling Changes. The remote likely does not exist.")
            self.console.error("Run `git remote add origin https://example.org` to add the remote.")
            self.console.error(
                "Or disable this feature by setting git.mode to either `local` or `disabled` in config.yaml")
            raise GitError("Error Pulling changes, remote does not exist.") from e

        try:
            pull_result: IterableList[FetchInfo] = self.repo.git.pull()
            self.console.info(pull_result)
        except GitCommandError:
            GitError(f"Git pull failed.").warn_and_continue(self.console)

    def git_init(self):
        """Runs git init in the `todo_folder`."""
        try:
            Repo(self.todo_folder).init()
        except Exception as e:
            self.console.error("Error running git init")
            self.console.error(f"{e}")

    def git_clone(self, repo_url: str):
        """Clone an existing repo from `repo_url`."""
        Repo.clone_from(repo_url, self.todo_folder)

    def commit_and_push(self, action: str):
        """
        Commit and push the files (if configured to do so).

        :param action: The name of the action, such as list or add.
        """
        if self.__git_mode is GitHandler.GitModeEnum.disabled:
            return

        if self.repo.is_dirty():
            self._commit(action)
            self._push()
        else:
            # git repo is not dirty, we do not have to commit anything.
            self.console.info("Nothing changed, nothing to commit or push.")

    def _push(self):
        if self.__git_mode is GitHandler.GitModeEnum.full:
            # Git push.
            try:
                result = self.repo.remote().push()
                result.raise_if_error()
                self.console.info(f"Push successful: {result[0].summary}")
            except GitCommandError as e:
                GitError(f"Push failed. {e.stderr}").warn_and_continue(self.console)

    def _commit(self, action):
        self.repo.index.add('*')
        try:
            # .dot files are not added...
            from todotree.Managers.RecurManager import RecurManager  # Adding globally causes a circular dependency.
            self.repo.index.add(RecurManager.recur_timestamp_filename)
        except:
            # File does not exist / Feature is not used.
            pass

        # Git commit.
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_commit = self.repo.index.commit(message=time + " " + action)
        self.console.info(f"Commit added: [{new_commit.hexsha[0:7]}] {new_commit.message} ")
        self.console.info(f"{new_commit.stats.total['files']} file(s) changed, "
                          f"{new_commit.stats.total['insertions']} insertions(+) "
                          f"{new_commit.stats.total['deletions']} deletions(-).")

    def apply_to_dict(self, dict_to_modify: dict):
        dict_to_modify['mode'] = str(self.git_mode.name)
        dict_to_modify['pull_delay'] = self.pull_time_minutes

    def read_from_dict(self, new_values: dict):
        self.git_mode = new_values.get("mode", self.git_mode)
        self.pull_time_minutes = new_values.get("pull_delay", self.pull_time_minutes)

    def run_raw_command(self, command: str) -> tuple[str, str]:
        """
        Run raw git commands, ie. if command is "status", the output would be the same as `git status`.
        :param command: The git command to run.
        """
        proc = subprocess.Popen(["git " + command], cwd=self.todo_folder, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        return (stdout.decode("utf-8"), stderr.decode("utf-8"))

    def __repr__(self):
        return f"GitHandler({self.__git_mode}, {self.pull_time_minutes}, {self.todo_folder})"
