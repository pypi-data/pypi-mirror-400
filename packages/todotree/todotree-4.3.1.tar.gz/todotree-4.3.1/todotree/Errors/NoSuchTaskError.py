from todotree.Errors.TodotreeError import TodotreeError


class NoSuchTaskError(TodotreeError):
    """Class representing when the task does not exist in the database."""
    pass

