# Adding tasks with `next`

Although Markdown files are easy enough to edit, sometimes you don't have your
project's task files open in an editor and just want to quickly capture a
thought or bug.

By default `next fix that thing` will add to `tasks.md` in your home
directory.

But `whatnext` is designed around projects having their own files, so there
are shortcuts to facilitate this.


## Choosing the task file

The _first word_ of your task text can be used to specify a destination.
It will use the first match it finds in this order:

1.  It uses a matching filename with an absolute path (`/path/to/tasks.md`)
2.  It uses a matching filename in the current directory
3.  It uses a matching filename in `$WHATNEXT_PROJECT_DIR`
4.  It uses a matching filename in `$HOME`
5.  If it matches a project directory in `$WHATNEXT_PROJECT_DIR`:
        1.  ...and the _second word_ matches an existing tasks file
            (eg. `$WHATNEXT_PROJECT_DIR/[project]/tasks/[word].md`)
            it uses that file
        2.  It uses the file `[project]/tasks.md` even if it doesn't exist yet
6.  Otherwise, it uses `$HOME/tasks.md` even if it doesn't exist yet

For example, with `$WHATNEXT_PROJECT_DIR` set to `~/projects`:

```bash
(computer)% next buy milk
Updated ~/tasks.md

(computer)% next alpha fix restart bug
Updated ~/projects/alpha/tasks.md

(computer)% next alpha backlog add some tests, dammit
Updated ~/projects/alpha/tasks/backlog.md
```


## Choosing where in the task file

Once the file is chosen, the file is checked for Markdown headings.

1.  If there are no headings, the task is added at the end of the file.
2.  If the _first remaining word_ matches (case-insensitive) a section of the
    file, the task is added to that section.
3.  Otherwise, the task is added at the top of the file ahead of
    the first heading (think of it as the inbox for new tasks when you
    are keeping them in sections).

If you would prefer the task is always added at the end of the file,
set `$WHATNEXT_APPEND_ONLY` to a value, or use `next -a`.
