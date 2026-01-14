# `whatnext` task formatting guide

## First, why?

I don't like the disconnect of details *about* a project not being *in*
the project itself. One source of truth. Not in a task manager, not GitHub
issues, not my inbox, not postit notes on a wall. Things about the code
*live with* the code.

For example:

- as a new feature is designed, the notes and implementation detail live
  alongside the task list
- an [architecture decision record][adr] could also contain the tasks needed
  to implement the decision so it would be even clearer whether or not it is
  now in force or still speculative
- abstract future ideas can be easily captured but deferred until the bulk of
  the current outstanding work is done so they don't overwhelm

By scanning the project directory for Markdown files, I am not restricted to
having one massive `todo.txt` file. By adding simple search and
prioritisation, I can keep some level of organisation without going overboard.
And by keeping it in plain text, any other tool can potentially use the same
task list.

Even though I do use a task manager ([Things][th] by Cultured Code),
I only keep short reminders about features there. Implementation details,
bugs, reminders, ideas, all stay in the project.

And if I ever needed a much bigger [Gantt chart][gc], I can still use Markdown
links to point to the project manager's inbox and then include a picture of a
kitten to make me feel better.


## how?

First, [install whatnext](installation.md). Second, create your task file(s).

Individual tasks use an expanded form of the GitHub style of task list,
[indicating more states](basics.md) than just done/not done.

There is an implicit importance to tasks from their position in the files, and
by files being ordered by depth, so tasks in `outstanding.md` will appear
before `projects/alpha.md`. This can be
[amplified with Markdown emphasis](prioritisation.md) to give different
levels of prioritisation.

If a task should be done by a specific date, and can otherwise be ignored
until near the date, [deadlines can be added](deadlines.md) which have a
configurable imminence window. Imminent tasks are more important than normal
priority. Overdue tasks have the highest priority.

If there is a useful prompt to include in `whatnext` output, task files
and sections can have [annotations included](annotations.md).

If a task has a dependency on other tasks, such that it cannot be done in any
order, you can [defer tasks](deferring.md) until all/some other tasks are complete.

If you need to exclude out some Markdown files for any reason, there are
[two ways to do that](exclusions.md).

Here's the full [whatnext usage and arguments](usage.md) guide.


## and how do I add tasks?

Well, they're Markdown files, manage them however you like. But if you really
need a quick way to add a task from the CLI, check out [next](next.md).


[th]: https://culturedcode.com/things/
[adr]: https://github.com/joelparkerhenderson/architecture-decision-record
[gc]: https://en.wikipedia.org/wiki/Gantt_chart
