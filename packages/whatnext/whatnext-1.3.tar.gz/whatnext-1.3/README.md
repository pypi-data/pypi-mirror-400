# What next?

I like to keep tasks in Markdown files. That way they can be interspersed
within instructions, serving as reminders, FIXMEs, and other todos.

All the features for enhancing your task lists are discussed in detail in
[the documentation](docs/index.md).

Document your tasks using an expanded version of the original
[GitHub task list notation][sn]:

```markdown
- [ ] open, this task is outstanding
- [/] in progress, this task is partially complete
- [X] complete, this task has been finished
- [#] cancelled, this task has been scratched
- [<] blocked, this task needs more input

- [ ] _an important task_

# **Make apple pie from scratch**
- [ ] invent the universe

# Things for later

- [ ] get NYE fireworks tickets @2025-12-31
- [ ] but in the end it doesn't even matter @after
```

Then install `whatnext`:

```bash
pip install whatnext
```

Now run it and it'll tell you what's next, sorting by priority and state:

```bash
(computer)% whatnext
README.md:
    # What next? / HIGH
    - [ ] a lot more important

README.md:
    # What next? / MEDIUM
    - [ ] a little more important

README.md:
    # What next? / IMMINENT 6d
    - [ ] get NYE fireworks tickets

README.md:
    # What next?
    - [/] in progress, this task is partially complete
    - [ ] open, this task is outstanding
    - [<] blocked, this task needs more input
```

Also provided, `next` to add tasks to files.

```bash
# by default, adds to $HOME/tasks.md
(computer)% next Add more features to whatnext
Updated tasks.md
```

[sn]: https://blog.github.com/2013-01-09-task-lists-in-gfm-issues-pulls-comments/
