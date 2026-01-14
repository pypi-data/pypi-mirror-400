# Deferring tasks

Some tasks either can't or won't be considered until some other tasks
are done, so you can indicate that these tasks _should not show up_ yet:

    # Someday

    @after

    - [ ] rewrite everything in Rust

`@after` on a line by itself applies to the whole file, on a header it
applies to the section, and on a task only applies to that task.


## After ... what?

Without any clarification, any deferred tasks will only appear in `whatnext`
output once every other non-deferred task is completed.

If you are trying to define project dependencies, you can indicate this
by naming the other task file(s):

    # Stage three

    @after stage_one.md stage_two.md

    - [ ] design the booster separation

Filenames are compared against all task files found, without considering
the directory they are in.

Circular dependencies (where A depends on B and B depends on A) will
cause an error showing the cycle. Referencing a nonexistent file will
produce a warning.

Running `whatnext --all` will always show the tasks regardless.
