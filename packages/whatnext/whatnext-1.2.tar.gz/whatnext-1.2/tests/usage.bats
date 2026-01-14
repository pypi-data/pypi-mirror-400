bats_require_minimum_version 1.5.0

@test "-h returns short usage" {
    run --separate-stderr \
        whatnext \
            -h

    expected_output=$(sed -e 's/^        //' <<"        EOF"
        Usage: whatnext [-h] [--help] [--version] [--guide] [--dir DIR] [-s] [-e]
                        [--relative] [-a] [--config CONFIG] [--ignore PATTERN] [-q]
                        [-o] [-p] [-b] [-d] [-c] [--priority LEVEL]
                        [--color | --no-color]
                        [match ...]
        EOF
    )
    diff -u <(echo "$expected_output") <(echo "$output")
    [ $status -eq 0 ]
}

@test "--help returns long usage" {
    run --separate-stderr \
        whatnext \
            --help

    expected_output=$(sed -e 's/^        //' <<"        EOF"
        Usage: whatnext [-h] [--help] [--version] [--guide] [--dir DIR] [-s] [-e]
                        [--relative] [-a] [--config CONFIG] [--ignore PATTERN] [-q]
                        [-o] [-p] [-b] [-d] [-c] [--priority LEVEL]
                        [--color | --no-color]
                        [match ...]

        List tasks found in Markdown files

        Positional arguments:
          match                filter results:
                                   [file/dir] - only include results from files within
                                   [string]   - only include tasks with this string in the
                                                task text, or header grouping
                                   [n]        - limit to n results, in priority order
                                   [n]r       - limit to n results, selected at random

        Options:
          -h                   Show the usage reminder and exit
          --help               Show this help message and exit
          --version            show program's version number and exit
          --guide              Show the Markdown formatting guide and exit
          --dir DIR            Directory to search (default: WHATNEXT_DIR, or '.')
          -s, --summary        Show summary of task counts per file
          -e, --edit           Open matching files in your editor (WHATNEXT_EDITOR,
                               VISUAL, EDITOR, or vi)
          --relative           Show selected states relative to all others (use with
                               --summary)
          -a, --all            Include all tasks and files, not just incomplete
          --config CONFIG      Path to config file (default: WHATNEXT_CONFIG, or
                               '.whatnext' in --dir)
          --ignore PATTERN     Ignore files matching pattern (can be specified
                               multiple times)
          -q, --quiet          Suppress warnings (or set WHATNEXT_QUIET)
          -o, --open           Show only open tasks
          -p, --partial        Show only in progress tasks
          -b, --blocked        Show only blocked tasks
          -d, --done           Show only completed tasks
          -c, --cancelled      Show only cancelled tasks
          --priority LEVEL     Show only tasks of this priority (can be specified
                               multiple times)
          --color, --no-color  Force colour output (or WHATNEXT_COLOR=1/0)

        Use --guide for Markdown formatting help.
        EOF
    )
    diff -u <(echo "$expected_output") <(echo "$output")
    [ $status -eq 0 ]
}

@test "--guide returns formatting guide" {
    run --separate-stderr \
        whatnext \
            --guide

    diff -u whatnext/guide.txt <(echo "$output")
    [ $status -eq 0 ]
}
