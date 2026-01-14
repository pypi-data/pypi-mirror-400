bats_require_minimum_version 1.5.0

@test "we call tasks 'tasks' not 'todos'" {
    # whatnext terminology is "tasks" not "todos", and I keep forgetting;
    # enforce the use of tasks, except where it is used legitimately
    run rg -c todo .
    output=$(echo "$output" | sort)

    expected_output=$(sed -e 's/^        //' <<"        EOF"
        ./README.md:1
        ./docs/index.md:1
        ./pyproject.toml:1
        ./tests/housekeeping.bats:3
        EOF
    )
    diff -u <(echo "$expected_output") <(echo "$output")
    [ $status -eq 0 ]
}

@test "guide.txt has no long lines" {
    long_lines=$(awk 'length > 79' whatnext/guide.txt | wc -l)
    [ "$long_lines" -eq 0 ]
}

@test "all --help arguments are documented in usage.md" {
    # extract long-form arguments from --help output
    help_args=$(whatnext --help \
        | grep -oE -- '--[a-z][-a-z]*' \
        | sort -u)

    missing=""
    for arg in $help_args; do
        if ! grep -q -- "$arg" docs/usage.md; then
            missing="$missing $arg"
        fi
    done

    [ -z "$missing" ] || {
        echo "Arguments missing from docs/usage.md:$missing"
        false
    }
}
