import argparse
from importlib.metadata import version
import os
from textwrap import dedent


def rewind_insertion_point(lines, position, min_position):
    first_non_blank = None
    while position > min_position:
        line = lines[position - 1]
        if line.startswith("- ["):
            return position, True
        if line.strip() != "":
            first_non_blank = position
        position -= 1
    if first_non_blank is not None:
        return first_non_blank, False
    return min_position, False


def update_file(file, line, content, message):
    try:
        with open(file, "r") as handle:
            lines = handle.readlines()
    except FileNotFoundError:
        lines = []
    lines.insert(line, content)
    with open(file, "w") as handle:
        handle.writelines(lines)
    print(message)


def display_path(path):
    home = os.path.realpath(os.environ["HOME"])
    real_path = os.path.realpath(path)
    if real_path.startswith(home):
        return "~" + real_path[len(home):]
    return path


def resolve_tasks_file(args):
    project_dir = os.environ.get("WHATNEXT_PROJECT_DIR")

    if len(args) > 1 and args[0].endswith(".md"):
        # explicit reference to file
        if os.path.isabs(args[0]):
            tasks_file = args[0]
            if os.path.isfile(tasks_file):
                return tasks_file, args[1:], display_path(tasks_file)
        else:
            # check relative to current dir ...
            if os.path.isfile(args[0]):
                tasks_file = os.path.abspath(args[0])
                return tasks_file, args[1:], display_path(tasks_file)
            # ... relative to $WHATNEXT_PROJECT_DIR ...
            if project_dir:
                tasks_file = os.path.join(project_dir, args[0])
                if os.path.isfile(tasks_file):
                    return tasks_file, args[1:], display_path(tasks_file)
            # ... relative to $HOME
            tasks_file = os.path.join(os.environ["HOME"], args[0])
            if os.path.isfile(tasks_file):
                return tasks_file, args[1:], display_path(tasks_file)

    # try shorthand references to file
    if project_dir and len(args) > 1:
        project_path = os.path.join(project_dir, args[0])
        if os.path.isdir(project_path):
            if len(args) > 2:
                subfile = os.path.join(project_path, "tasks", f"{args[1]}.md")
                if os.path.isfile(subfile):
                    return subfile, args[2:], display_path(subfile)
            tasks_file = os.path.join(project_path, "tasks.md")
            return tasks_file, args[1:], display_path(tasks_file)

    # default ~/tasks.md
    tasks_file = os.path.join(os.environ["HOME"], "tasks.md")
    return tasks_file, args, display_path(tasks_file)


def main():
    parser = argparse.ArgumentParser(
        prog="next",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Add a task to a Markdown (.md file) task list.",
        epilog=dedent("""\
            The file to add to is chosen indirectly:

            - if the first word of text is an absolute filename, use that
            - if the first word matches a file in the current directory, use that
            - if the first word matches a file in $WHATNEXT_PROJECT_DIR, use that
            - if the first word matches a file in $HOME, use that
            - if the first word matches a directory in $WHATNEXT_PROJECT_DIR:
                - if the second word matches a file
                  $WHATNEXT_PROJECT_DIR/[project]/tasks/[word].md then use that
                - otherwise, use $WHATNEXT_PROJECT_DIR/[project]/tasks.md
            - otherwise, use $HOME/tasks.md

            With the remaining text:

            - if the file uses headings to section the file:
                - if the first word case-insensitively matches a heading in the
                  file, the task is added to that section
                - otherwise, the task is added above the first heading
            - otherwise, the task is added to the end of the file
            """),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"next {version('whatnext')}",
    )
    parser.add_argument(
        "-a",
        dest="append_only",
        action="store_true",
        help="append to end of file, ignoring headings (or set WHATNEXT_APPEND_ONLY)",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="task text to add",
    )
    parsed = parser.parse_args()

    if not parsed.text:
        return

    args = parsed.text
    append_only = parsed.append_only
    tasks_file, args, display_path = resolve_tasks_file(args)

    task = f"- [ ] {' '.join(args)}\n"
    if not os.path.isfile(tasks_file):
        update_file(tasks_file, 0, task, f"Created {display_path}")
        return

    with open(tasks_file, "r") as handle:
        lines = handle.readlines()

    if append_only or os.environ.get("WHATNEXT_APPEND_ONLY"):
        position, found_task = rewind_insertion_point(lines, len(lines), 0)
        if found_task:
            update_file(tasks_file, position, task, f"Updated {display_path}")
        else:
            update_file(tasks_file, len(lines), f"\n{task}", f"Updated {display_path}")
        return

    headers = [
        (index, line) for index, line
            in enumerate(lines)
                if line.startswith("#")
    ]

    if not headers:
        update_file(tasks_file, len(lines), task, f"Updated {display_path}")
        return

    for index, (line_num, line) in enumerate(headers):
        if line.lstrip("#").strip().lower() != args[0].lower():
            continue

        section_end = headers[index + 1][0] if index + 1 < len(headers) else len(lines)
        section_name = line.lstrip("#").strip()
        message = f"Updated {display_path} ({section_name})"
        task = f"- [ ] {' '.join(args[1:])}\n"

        position, found_task = rewind_insertion_point(lines, section_end, line_num + 1)
        if found_task:
            update_file(tasks_file, position, task, message)
        else:
            update_file(tasks_file, position, f"\n{task}", message)
        return

    # no matching header, insert before first header
    position, found_task = rewind_insertion_point(lines, headers[0][0], 0)
    if found_task:
        update_file(tasks_file, position, task, f"Updated {display_path}")
    else:
        update_file(tasks_file, headers[0][0], f"{task}\n", f"Updated {display_path}")
