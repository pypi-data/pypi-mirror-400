bats_require_minimum_version 1.5.0

function setup {
    cp -r "$BATS_TEST_DIRNAME/next/." "$BATS_TEST_TMPDIR"
    export HOME="$BATS_TEST_TMPDIR"
    export WHATNEXT_PROJECT_DIR="$BATS_TEST_TMPDIR/projects"
}

@test "shows version" {
    run next --version

    [[ "$output" =~ ^next\ [0-9]+\. ]]
    [ $status -eq 0 ]
}

@test "shows usage" {
    expected_output=$(sed -e 's/^        //' <<"        EOF"
        usage: next [-h] [--version] [-a] [text ...]

        Add a task to a Markdown (.md file) task list.

        positional arguments:
          text        task text to add

        options:
          -h, --help  show this help message and exit
          --version   show program's version number and exit
          -a          append to end of file, ignoring headings (or set
                      WHATNEXT_APPEND_ONLY)

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
        EOF
    )

    run next --help

    diff -u <(echo "$expected_output") <(echo "$output")
    [ $status -eq 0 ]
}

@test "without args does nothing" {
    expected_output=$(sed -e 's/^        //' <<"        EOF"
        # Tasks

        - [ ] existing task
        EOF
    )

    run next

    diff -u <(echo "$expected_output") "$HOME/tasks.md"
    [ $status -eq 0 ]
}

@test "non-markdown file is treated as part of text" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        - [ ] something.txt do something

        # Tasks

        - [ ] existing task
        EOF
    )

    run next something.txt do something

    diff -u "$BATS_TEST_DIRNAME/next/something.txt" "$HOME/something.txt"
    diff -u <(echo "$expected_content") "$HOME/tasks.md"
    [ "$output" = "Updated ~/tasks.md" ]
    [ $status -eq 0 ]
}

@test "nonexistent file is treated as part of text" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        - [ ] nonexistent.md do something

        # Tasks

        - [ ] existing task
        EOF
    )

    run next nonexistent.md do something

    diff -u <(echo "$expected_content") "$HOME/tasks.md"
    [ "$output" = "Updated ~/tasks.md" ]
    [ $status -eq 0 ]
}

function assert_task_added {
    local tasks_file="$1"
    local expected_output="$2"

    expected_content=$(sed -e 's/^        //' <<"        EOF"
        - [ ] do something

        # Tasks

        - [ ] existing task
        EOF
    )

    diff -u <(echo "$expected_content") "$tasks_file"
    [ "$output" = "$expected_output" ]
    [ $status -eq 0 ]
}

@test "adds to master task list" {
    run next do something

    assert_task_added \
        "$HOME/tasks.md" \
        "Updated ~/tasks.md"
}

@test "adds to master task list wherever you are" {
    cd "$WHATNEXT_PROJECT_DIR"
    run next do something

    assert_task_added \
        "$HOME/tasks.md" \
        "Updated ~/tasks.md"
}

@test "adds to master task list from outside of homedir" {
    cd /tmp
    run next do something

    assert_task_added \
        "$HOME/tasks.md" \
        "Updated ~/tasks.md"
}

@test "adds to existing project" {
    run next alpha do something

    assert_task_added \
        "$WHATNEXT_PROJECT_DIR/alpha/tasks.md" \
        "Updated ~/projects/alpha/tasks.md"
}

@test "adds to existing project from outside of homedir" {
    cd /tmp
    run next alpha do something

    assert_task_added \
        "$WHATNEXT_PROJECT_DIR/alpha/tasks.md" \
        "Updated ~/projects/alpha/tasks.md"
}

@test "adds to master task list without WHATNEXT_PROJECT_DIR" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        - [ ] alpha do something

        # Tasks

        - [ ] existing task
        EOF
    )
    unset WHATNEXT_PROJECT_DIR

    run next alpha do something

    diff -u <(echo "$expected_content") "$HOME/tasks.md"
    [ "$output" = "Updated ~/tasks.md" ]
    [ $status -eq 0 ]
}

@test "adds to project task file" {
    run next alpha things do something

    assert_task_added \
        "$WHATNEXT_PROJECT_DIR/alpha/tasks/things.md" \
        "Updated ~/projects/alpha/tasks/things.md"
}

@test "adds to project task file from outside of homedir" {
    cd /tmp
    run next alpha things do something

    assert_task_added \
        "$WHATNEXT_PROJECT_DIR/alpha/tasks/things.md" \
        "Updated ~/projects/alpha/tasks/things.md"
}

@test "creates project tasks file" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        - [ ] do something
        EOF
    )

    run next beta do something

    diff -u <(echo "$expected_content") "$WHATNEXT_PROJECT_DIR/beta/tasks.md"
    [ "$output" = "Created ~/projects/beta/tasks.md" ]
    [ $status -eq 0 ]
}

@test "does not add to things.md as it is not tried" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        - [ ] things do something
        EOF
    )

    run next beta things do something

    diff -u <(echo "$expected_content") "$WHATNEXT_PROJECT_DIR/beta/tasks.md"
    [ "$output" = "Created ~/projects/beta/tasks.md" ]
    [ $status -eq 0 ]
}

@test "add to alternate file" {
    run next alternate.md do something

    assert_task_added \
        "$HOME/alternate.md" \
        "Updated ~/alternate.md"
}

@test "add with absolute filename" {
    cd /tmp
    run next "$HOME/alternate.md" do something

    assert_task_added \
        "$HOME/alternate.md" \
        "Updated ~/alternate.md"
}

@test "add with relative filename" {
    cd $HOME/projects
    run next alpha/tasks/things.md do something

    assert_task_added \
        "$HOME/projects/alpha/tasks/things.md" \
        "Updated ~/projects/alpha/tasks/things.md"
}

@test "add with homedir relative filename from outside of home" {
    # this works because any relative filename where that filename
    # doesn't exist is then tried relative to $HOME
    cd /tmp
    run next projects/alpha/tasks/things.md do something

    assert_task_added \
        "$HOME/projects/alpha/tasks/things.md" \
        "Updated ~/projects/alpha/tasks/things.md"
}

@test "add with project relative filename from outside of home" {
    # this works because any relative filename where that filename
    # doesn't exist is then tried relative to $HOME and then
    # $WHATNEXT_PROJECT_DIR
    cd /tmp
    run next alpha/tasks/things.md do something

    assert_task_added \
        "$HOME/projects/alpha/tasks/things.md" \
        "Updated ~/projects/alpha/tasks/things.md"
}

@test "adds to end of file" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"




        - [ ] do something
        EOF
    )

    run next empty.md do something

    diff -u <(echo "$expected_content") "$HOME/empty.md"
    [ "$output" = "Updated ~/empty.md" ]
    [ $status -eq 0 ]
}

@test "test within file positioning" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        This is an explanation.

        This section currently has no tasks.

        - [ ] do something

        # First

        - [ ] first something

        # Second

        - [ ] second something

        #### Third

        This section contains notes.

        - [ ] third something

        ## Fourth

        A note.

        - [ ] A task.
        - [ ] Another task.

        Another note.

        # Second

        There is no way to add a task here.

        # Last

        - [ ] second to last task
        - [ ] last task
        EOF
    )

    run next insert.md do something
    run next insert.md first first something
    run next insert.md second second something
    run next insert.md third third something
    run next insert.md fourth Another task.
    run next insert.md last last task

    diff -u <(echo "$expected_content") "$HOME/insert.md"
    [ "$output" = "Updated ~/insert.md (Last)" ]
    [ $status -eq 0 ]
}

@test "WHATNEXT_APPEND_ONLY set" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        # Tasks

        - [ ] existing task
        - [ ] do something
        EOF
    )
    export WHATNEXT_APPEND_ONLY=1

    run next do something

    diff -u <(echo "$expected_content") "$HOME/tasks.md"
    [ "$output" = "Updated ~/tasks.md" ]
    [ $status -eq 0 ]
}

@test "append flag" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        # Tasks

        - [ ] existing task
        - [ ] do something
        EOF
    )

    run next -a do something

    diff -u <(echo "$expected_content") "$HOME/tasks.md"
    [ "$output" = "Updated ~/tasks.md" ]
    [ $status -eq 0 ]
}

@test "appending spaces out tasks" {
    expected_content=$(sed -e 's/^        //' <<"        EOF"
        # Tasks

        This is where things get added.

        - [ ] do something
        EOF
    )

    run next -a append.md do something

    diff -u <(echo "$expected_content") "$HOME/append.md"
    [ "$output" = "Updated ~/append.md" ]
    [ $status -eq 0 ]
}
