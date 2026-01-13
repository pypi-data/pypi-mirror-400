# todotree

[![Latest Release](https://gitlab.com/chim1aap/todotree/-/badges/release.svg)](https://gitlab.com/chim1aap/todotree/-/releases) 
[![pipeline status](https://gitlab.com/chim1aap/todotree/badges/master/pipeline.svg)](https://gitlab.com/chim1aap/todotree/-/commits/master) 
[![License](https://img.shields.io/gitlab/license/chim1aap/todotree)](https://img.shields.io/gitlab/license/chim1aap/todotree)

A [todo.txt](http://todotxt.org/) implementation with more features:

- Define task dependency using the `bl:` and `by:` keywords.
- Hide tasks until a certain date using the `t:` keyword.
- Define due dates for tasks with the `due:` keyword.
- `git` integration.

- **GitLab repository**: <https://gitlab.com/chim1aap/todotree/>
- **Documentation** <https://chim1aap.gitlab.io/todotree/>

## Installation

To use the interactive setup, install the package using:
```shell
pip install todotree[init]
```

To install the package on another machine, use `pip install todotree`. 
This does not have the init dependencies.

### Interactively

To create the files interactively, use `todotree init`. 
The app will ask you a few questions about the features you want to enable and the locations of the files.
It will then generate the files at the correct locations, and you can use todotree.

### Manually

If you do not want to use the interactive version, you can run it manually. The commands are as follows:

```shell
mkdir -p ~/.local/share/todotree/
touch ~/.local/share/todotree/todo.txt
touch ~/.local/share/todotree/done.txt
touch ~/.local/share/todotree/config.yaml
```

To make use of the `git` versioning, the following steps need to be done.

1. install `git`.
2. run `git init` in the directory where the todo.txt and done.txt are. (ie `~/local/share/todotree`)
3. run `git remote add origin <url>` to add a remote repository. Note that the remote needs to be configured.
4. Set the `git_mode` in the configuration to `Full`.
5. run a todotree command which edits the files, such as `edit`. This will push the data to the remote repository.

## Screenshots

projects

![project](img/projecttree-example.png)

context

![context](img/contexttree-example.png)

---

Repository initiated with [fpgmaas/cookiecutter-poetry](https://github.com/fpgmaas/cookiecutter-poetry).
