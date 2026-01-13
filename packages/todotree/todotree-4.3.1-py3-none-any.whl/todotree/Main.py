# NOTE: this file cannot be in a class. See: https://github.com/pallets/click/issues/601
# https://click.palletsprojects.com/en/8.1.x/commands/#nested-handling-and-contexts
import click

# Commands are imported when the function is run, to increase performance.
from todotree.Managers.TaskManager import TaskManager
from todotree.Config.Config import Config
from todotree.MainUtils import MainUtils


@click.group()
@MainUtils.common_options
def root(ctx: click.Context, **kwargs):
    """
    The main list of todotree's command.

    For more information on a command, use `todotree COMMAND --help`.
    """
    # ^ This text also shows up in the help command.
    # Parse options given before the command.
    # So the `--todo-file task.txt` option in the help text example.
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config()
    MainUtils.parse_common_options(ctx.obj["config"], **kwargs)


@root.command("add", short_help="Add a task to the task list")
@click.argument("task", type=str, nargs=-1)
@MainUtils.common_options
def add(ctx: click.Context, task: tuple, **kwargs):
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Add import Add

    Add(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(task)


@root.command("addx", short_help="Add a task and immediately mark it as done")
@click.argument("task", type=str, nargs=-1)
@MainUtils.common_options
def add_x(ctx: click.Context, task: tuple, **kwargs):
    """
    Adds a completed task to done.txt. The task is not added to todo.txt.
    :param task: The task to add to done.txt.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.AddX import AddX

    AddX(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(task)


@root.command("append", short_help="Append `append_string` to `task_nr`")
@click.argument("task_nr", type=int)
@click.argument("append_string", type=str, nargs=-1)
@MainUtils.common_options
def append(ctx: click.Context, task_nr: int, append_string: tuple[str], **kwargs):
    """
    Appends the contents of append_string to the task represented by task_nr.
    A space is inserted between the two tasks, so you do not have to worry that words aretogether.

    Example: todotree append 1 "some text"
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Append import Append

    Append(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(task_nr, append_string)


@root.command("cd", short_help="Print directory of the todo.txt directory")
@MainUtils.common_options
def cd(ctx: click.Context, **kwargs):
    """print directory of the todo.txt directory"""
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Cd import Cd

    Cd(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("compress", short_help="Removes newlines from the todo.txt, thereby compressing the file.")
@MainUtils.common_options
def compress(ctx: click.Context, **kwargs):
    """print directory of the todo.txt directory"""
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Compress import Compress

    Compress(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("context", short_help="List task in a tree, by context")
@MainUtils.common_options
def context(ctx: click.Context, **kwargs):
    """list a tree, of which the first node is the context, the second nodes are the tasks"""
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Context import Context

    Context(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("do", short_help="Mark task as done and move it to the done.txt")
@click.argument("task_numbers", type=list, nargs=-1)  # type=list[int]
@MainUtils.common_options
def do(ctx: click.Context, task_numbers: list[tuple], **kwargs):
    """
    Mark tasks as done, therefor moving them to done.txt with a date stamp of today.
    :param task_numbers: The list of tasks which are completed.
    """

    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Do import Do

    Do(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(task_numbers)


@root.command("due", short_help="List tasks by their due date")
@MainUtils.common_options
def due(ctx: click.Context, **kwargs):
    """List tasks in a tree by their due date."""
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Due import Due

    Due(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("edit", short_help="Open the todo.txt in an editor.")
@click.argument("file", default="todo",
                type=click.Choice(["todo", "done", "stale", "recur"]))
@MainUtils.common_options
def edit(ctx: click.Context, **kwargs):
    """
    Open the file in an editor for manual editing of tasks.

    This is useful when you need to modify a lot of tasks, which would be complicated when doing it with todotree.
    The second argument defines which file you want to edit, defaults to todo.txt.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Edit import Edit

    Edit(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(kwargs["file"])


@root.command("filter", short_help="Only show tasks containing the search term.")
@click.argument("search_term")
@MainUtils.common_options
def filter_list(ctx: click.Context, search_term, **kwargs):
    """
    Only show tasks which have search term in them. This can also be a keyword.

    :param search_term: The term to search.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Filter import Filter

    Filter(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(search_term)


@root.command("git", short_help="Run git commands natively.")
@click.argument("command", nargs=-1)
@MainUtils.common_options
def git(ctx: click.Context, command, **kwargs):
    """
    Run git commands directly. This is the same as `git -C $(todotree cd) command`.
    This is particulary useful if you are in a merge conflict.

    :param command: command arguments to be passed to `git`. This command may have any number of spaces or flags.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Git import Git
    # Convert tuple to string.
    command = " ".join(command)

    Git(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(command)



@root.command("help", short_help="Print help text.")
@click.pass_context
def help_text(ctx: click.Context):
    print(ctx.parent.get_help())


@root.command("init", short_help="Initialize folder for first use.")
@MainUtils.common_options
def init(ctx: click.Context, **kwargs):
    """
    Initializes the files and folders needed for a functioning todotree according to the user's prompts.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Init import Init

    Init().run()


@root.command("list", short_help="List tasks")
@MainUtils.common_options
def list_tasks(ctx: click.Context, **kwargs):
    """
    Print a flat list of tasks, sorted by their priority.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.List import List

    MainUtils.parse_common_options(ctx.obj["config"], **kwargs)
    List(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("list_done", short_help="List tasks which are marked as done")
@MainUtils.common_options
def list_done(ctx: click.Context, **kwargs):
    """
    List tasks which are marked as done. The numbers can be used with the revive command.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.ListDone import ListDone

    ListDone(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("print_raw", short_help="Print todo.txt without any formatting or filtering")
@MainUtils.common_options
def print_raw(ctx: click.Context, **kwargs):
    """
    Output the todo.txt without any processing.
    This is equivalent to `cat $(todo cd)/todo.txt` in bash.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.PrintRaw import PrintRaw

    PrintRaw(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("priority", short_help="Set new priority to task")
@click.argument("task_number", type=int)
@click.argument("new_priority", type=str)
@MainUtils.common_options
def priority(ctx: click.Context, task_number, new_priority, **kwargs):
    """
    Adds or updates the priority of the task.
    :param task_number: The task to re-prioritize.
    :param new_priority: The new priority.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Priority import Priority

    Priority(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(task_number, new_priority)


@root.command("project", short_help="Print tree by project")
@MainUtils.common_options
def project(ctx: click.Context, **kwargs):
    """
    Print the task list in a tree by project.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Project import Project

    Project(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("recur", short_help="Add recurring tasks defined in recur.txt")
@click.option("--date", help="Use this date instead of the one in the timestamp file.")
@MainUtils.common_options
def recur(ctx: click.Context, date: str | None, **kwargs):
    """
    Add tasks according to recur.txt.
    --date: Use this date instead of the one in the timestamp file.

    In recur.txt you can add tasks that have to be done periodically, such as doing taxes.
    The format in recur.txt is:

        `<start date> ; interval ; <end date> ; <task string>`

    The end date is optional. This is a valid line for example:
    2020-01-01 ; yearly ; (C) Celebrate the new year.

    This is certainly not the only program which can do these.
    Different solutions to this command exist, here are a few alternatives:
     - https://www.rememberthemilk.com/
     - https://github.com/smartlitchi/ice-recur
    You can use those with the `addons` command after installing a suitable addon script.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Recur import Recur
    Recur(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(date=date)


@root.command("revive", short_help="Revive a task that was accidentally marked as done.")
@click.argument("done_number", type=int)
@MainUtils.common_options
def revive(ctx: click.Context, done_number, **kwargs):
    """
    Move a task from done.txt to todo.txt.
    The `done_number` can be found using the `list_done` command.
    :param done_number: The number of the task to revive.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Revive import Revive

    Revive(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(done_number)


@root.command("schedule", short_help="Hide task until date.")
@click.argument("task_number", type=int)
@click.argument("new_date", type=str, nargs=-1)
@MainUtils.common_options
def schedule(ctx: click.Context, task_number: int, new_date: tuple[str], **kwargs):
    """
    hide the task until the date given. If new_date is not in ISO format (yyyy-mm-dd) such as "Next Wednesday",
    then it tries to figure out the date with the `date` program, which is only in linux.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Schedule import Schedule

    Schedule(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(new_date, task_number)


@root.group("stale", short_help="Manage the stale.txt task list.")
@MainUtils.common_options
def stale(ctx: click.Context, **kwargs):
    # process for stale.txt
    pass


@stale.command("list", short_help="List the stale tasks.")
@MainUtils.common_options
def stale_list(ctx: click.Context, **kwargs):
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Stale_list import StaleList
    StaleList(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@stale.command("revive", short_help="Move task from stale.txt to todo.txt")
@click.argument("task_number", type=int)
@MainUtils.common_options
def stale_revive(ctx: click.Context, task_number: int, **kwargs):
    """Remove task with index `task_number` from stale.txt and adds it back to todo.txt."""
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Stale_revive import StaleRevive
    StaleRevive(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(task_number)


@stale.command("add", short_help="Move task from todo.txt to stale.txt")
@click.argument("task_number", type=int)
@MainUtils.common_options
def stale_add(ctx: click.Context, task_number: int, **kwargs):
    """Removes the task with the index `task_number` from todo.txt and adds it to stale.txt."""
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Stale_add import StaleAdd
    StaleAdd(ctx.obj["config"], TaskManager(ctx.obj["config"])).run(task_number)


@root.command("version", short_help="Show the version of TodoTree.")
@MainUtils.common_options
def version(ctx: click.Context, **kwargs):
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Version import Version

    Version(ctx.obj["config"], TaskManager(ctx.obj["config"])).run()


@root.command("addons", short_help="Run an addon script", context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1, type=str)
@MainUtils.common_options
def addons_command(ctx: click.Context, command: str, **kwargs):
    """
    Run an addon script.
    The script must be in the addons_folder. It can be any language you like: It does not have to be python.
    However, it must have the executable bit set.

    :param command: The script/command to run.
    """
    MainUtils.initialize(ctx.obj["config"], **kwargs)
    from todotree.Commands.Addons import Addons

    Addons(ctx.obj["config"]).run(command)


#  End Region Command Definitions.
#  Setup Click

CONTEXT_SETTINGS: dict = dict(help_option_names=["-h", "--help"])
"""Click context settings. See https://click.palletsprojects.com/en/8.1.x/complex/ for more information."""
cli: click.CommandCollection = click.CommandCollection(sources=[root], context_settings=CONTEXT_SETTINGS)
"""Command Collection defining defaults. https://click.palletsprojects.com/en/8.1.x/api/#click.CommandCollection ."""

if __name__ == "__main__":
    cli(obj={})
