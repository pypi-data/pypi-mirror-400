bats_require_minimum_version 1.5.0

@test "circular dependency exits with error" {
    run --separate-stderr \
        whatnext \
            tests/deferring/circular-a.md \
            tests/deferring/circular-b.md

    expected_stderr=$(sed -e 's/^        //' <<"        EOF"
        ERROR: Circular dependency: circular-a.md -> circular-b.md -> circular-a.md
        EOF
    )
    diff -u <(echo "$expected_stderr") <(echo "$stderr")
    [ $status -eq 1 ]
}

@test "warning on nonexistent file dependency" {
    run --separate-stderr \
        whatnext \
            tests/deferring/missing-dep.md

    expected_stderr=$(sed -e 's/^        //' <<"        EOF"
        WARNING: tests/deferring/missing-dep.md: 'nonexistent.md' does not exist
        EOF
    )
    diff -u <(echo "$expected_stderr") <(echo "$stderr")
    [ $status -eq 0 ]
}

@test "all errors and warnings shown" {
    run --separate-stderr \
        whatnext \
            tests/deferring

    expected_stderr=$(sed -e 's/^        //' <<"        EOF"
        WARNING: missing-dep.md: 'nonexistent.md' does not exist
        ERROR: Circular dependency: circular-a.md -> circular-b.md -> circular-a.md
        EOF
    )
    diff -u <(echo "$expected_stderr") <(echo "$stderr")
    [ $status -eq 1 ]
}

@test "warning suppressed with --quiet" {
    run --separate-stderr \
        whatnext \
            --quiet \
            tests/deferring/missing-dep.md

    diff -u <(echo "") <(echo "$stderr")
    [ $status -eq 0 ]
}
