bats_require_minimum_version 1.5.0

@test "file can self-exclude" {
    WHATNEXT_CONFIG=.whatnext.all \
    WHATNEXT_DIR=example \
    WHATNEXT_TODAY=2025-01-01 \
        run --separate-stderr \
            whatnext \
                --all

    # template.md should not appear in output
    [ -z "$(echo "$output" | grep template.md)" ]
    [ $status -eq 0 ]
}

@test "explicit query ignores self-exclusion" {
    WHATNEXT_DIR=example \
    WHATNEXT_TODAY=2025-01-01 \
        run --separate-stderr \
            whatnext \
                --all \
                template.md

    expected_output=$(sed -e 's/^        //' <<"        EOF"
        example/template.md:
            # New Project Template
            - [ ] define project scope
            - [ ] identify stakeholders
            - [ ] create timeline
        EOF
    )
    diff -u <(echo "$expected_output") <(echo "$output")
    [ $status -eq 0 ]
}
