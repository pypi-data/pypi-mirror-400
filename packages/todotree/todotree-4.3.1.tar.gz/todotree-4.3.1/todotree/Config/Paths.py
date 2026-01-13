from pathlib import Path

import xdg_base_dirs
from todotree.Config.AbstractSubConfig import AbstractSubConfig


class Paths(AbstractSubConfig):
    """
    Configuration of the paths.
    Paths are calculated dynamically when not set.
    """

    def __init__(self):
        self.todo_folder: Path = xdg_base_dirs.xdg_data_home() / "todotree"
        """Path to the folder containing the data files."""
        self.__project_tree_folder: Path | None = None
        self.__todo_file: Path | None = None
        self.__done_file: Path | None = None
        self.__recur_file: Path | None = None
        self.__addons_folder: Path | None = None
        self.__stale_file: Path | None = None

    def read_from_dict(self, new_values: dict):
        self.todo_folder = Path(new_values.get('folder', self.todo_folder)).expanduser()

        if (todo_file := new_values.get('todo_file')) is not None:
            self.todo_file = Path(todo_file).expanduser()

        if (done_file := new_values.get('done_file')) is not None:
            self.done_file = Path(done_file).expanduser()

        if (recur_file := new_values.get('recur_file')) is not None:
            self.__recur_file = Path(recur_file).expanduser()

        if (stale_file := new_values.get('stale_file', None)) is not None:
            self.__stale_file = Path(stale_file).expanduser()

        if (project := new_values.get('project_folder')) is not None:
            self.__project_tree_folder = Path(project).expanduser()

        if (addons := new_values.get('addons_folder')) is not None:
            self.__addons_folder = Path(addons).expanduser()

    def apply_to_dict(self, dict_to_modify: dict):
        dict_to_modify['folder'] = str(self.todo_folder)
        dict_to_modify['todo_file'] = str(self.todo_file)
        dict_to_modify['done_file'] = str(self.done_file)
        dict_to_modify['recur_file'] = str(self.recur_file)
        dict_to_modify['stale_file'] = str(self.stale_file)
        dict_to_modify['project_folder'] = str(self.project_tree_folder)
        dict_to_modify['addons_folder'] = str(self.addons_folder)

    def __repr__(self):
        return (f"Paths({self.todo_folder}, "
                f"{self.todo_file}, {self.done_file}, {self.recur_file}, {self.addons_folder})")

    @property
    def todo_file(self) -> Path:
        """Path to the todo.txt file."""
        return self.__todo_file if self.__todo_file is not None else Path(self.todo_folder) / "todo.txt"

    @todo_file.setter
    def todo_file(self, new_path: Path):
        self.__todo_file = new_path

    @property
    def done_file(self) -> Path:
        """Path to the done.txt file."""
        return self.__done_file if self.__done_file is not None else Path(self.todo_folder) / "done.txt"

    @done_file.setter
    def done_file(self, new_path: Path):
        self.__done_file = new_path

    @property
    def recur_file(self) -> Path:
        """Path to the recur.txt file."""
        return self.__recur_file if self.__recur_file is not None else Path(self.todo_folder) / "recur.txt"

    @recur_file.setter
    def recur_file(self, new_recur_file: Path):
        self.__recur_file = new_recur_file

    @property
    def stale_file(self) -> Path:
        """Path to the stale.txt file."""
        return self.__stale_file if self.__stale_file is not None else Path(self.todo_folder) / "stale.txt"

    @property
    def addons_folder(self) -> Path:
        """Path to the addon folder."""
        return self.__addons_folder if self.__addons_folder is not None else Path(self.todo_folder) / "addons"

    @addons_folder.setter
    def addons_folder(self, new_path: Path):
        self.__addons_folder = new_path

    @property
    def project_tree_folder(self) -> Path:
        """Path to the folder containing the projects."""
        return self.__project_tree_folder if self.__project_tree_folder is not None else self.todo_folder / "projects"

    @project_tree_folder.setter
    def project_tree_folder(self, new_path: Path):
        self.__project_tree_folder = new_path
