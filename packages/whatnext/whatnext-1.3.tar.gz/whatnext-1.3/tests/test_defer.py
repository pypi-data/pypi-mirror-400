from datetime import date
from textwrap import dedent

import pytest

from whatnext.models import MarkdownFile, Priority, State
from whatnext.whatnext import (
    filter_deferred,
    check_dependencies,
    CircularDependencyError,
)


class TestAfterParsingOnTasks:
    def test_task_without_after(self):
        file = MarkdownFile(
            source_string="- [ ] normal task",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].text == "normal task"
        assert file.tasks[0].deferred is None

    def test_task_with_bare_after(self):
        file = MarkdownFile(
            source_string="- [ ] rewrite everything in Rust @after",
            today=date(2025, 1, 1),
        )
        assert len(file.tasks) == 1
        assert file.tasks[0].text == "rewrite everything in Rust"
        assert file.tasks[0].deferred == []

    def test_task_with_after_single_file(self):
        file = MarkdownFile(
            source_string="- [ ] design the booster @after stage_one.md",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].text == "design the booster"
        assert file.tasks[0].deferred == ["stage_one.md"]

    def test_task_with_after_multiple_files(self):
        file = MarkdownFile(
            source_string="- [ ] design the booster @after stage_one.md stage_two.md",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].text == "design the booster"
        assert file.tasks[0].deferred == ["stage_one.md", "stage_two.md"]

    def test_after_with_deadline(self):
        file = MarkdownFile(
            source_string="- [ ] task with both @2025-12-25 @after",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].text == "task with both"
        assert file.tasks[0].due == date(2025, 12, 25)
        assert file.tasks[0].deferred == []

    def test_after_consumes_remaining_text(self):
        file = MarkdownFile(
            source_string="- [ ] task reversed @after @2025-12-25",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].text == "task reversed"
        assert file.tasks[0].due is None
        assert file.tasks[0].deferred == ["@2025-12-25"]


class TestAfterParsingOnHeaders:
    def test_header_with_bare_after(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # Someday @after

                - [ ] rewrite everything in Rust
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].text == "rewrite everything in Rust"
        assert file.tasks[0].deferred == []

    def test_header_with_after_single_file(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # Stage three @after stage_one.md

                - [ ] design the booster separation
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].text == "design the booster separation"
        assert file.tasks[0].deferred == ["stage_one.md"]

    def test_header_with_after_multiple_files(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # Stage three @after stage_one.md stage_two.md

                - [ ] design the booster separation
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == ["stage_one.md", "stage_two.md"]

    def test_subsection_inherits_after(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # Someday @after

                ## Subtasks

                - [ ] subtask inherits deferral
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == []

    def test_new_section_resets_after(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # Someday @after

                - [ ] deferred task

                # Now

                - [ ] normal task
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == []
        assert file.tasks[1].deferred is None


class TestAfterParsingFileLevel:
    def test_file_level_bare_after(self):
        file = MarkdownFile(
            source_string=dedent("""\
                @after

                # Tasks

                - [ ] all tasks in file are deferred
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == []

    def test_file_level_after_with_files(self):
        file = MarkdownFile(
            source_string=dedent("""\
                @after prerequisites.md

                # Tasks

                - [ ] depends on prerequisites
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == ["prerequisites.md"]

    def test_file_level_after_anywhere_in_file(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # Tasks

                - [ ] still deferred

                @after
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == []

    def test_file_level_after_in_middle(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # First section

                - [ ] first task

                @after

                # Second section

                - [ ] second task
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == []
        assert file.tasks[1].deferred == []


class TestAfterOverrides:
    def test_task_overrides_section(self):
        file = MarkdownFile(
            source_string=dedent("""\
                # Deferred section @after stage_one.md

                - [ ] inherits section deferral
                - [ ] overrides with own deferral @after stage_two.md
                - [ ] overrides to wait for all @after
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == ["stage_one.md"]
        assert file.tasks[1].deferred == ["stage_two.md"]
        assert file.tasks[2].deferred == []

    def test_section_overrides_file(self):
        file = MarkdownFile(
            source_string=dedent("""\
                @after stage_one.md

                # Inherits file deferral

                - [ ] inherits from file

                # Overrides @after stage_two.md

                - [ ] inherits from section override

                # Removes deferral @after

                - [ ] now waits for all
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == ["stage_one.md"]
        assert file.tasks[1].deferred == ["stage_two.md"]
        assert file.tasks[2].deferred == []

    def test_task_overrides_file_level(self):
        file = MarkdownFile(
            source_string=dedent("""\
                @after prerequisites.md

                # Tasks

                - [ ] inherits file deferral
                - [ ] overrides file deferral @after other.md
            """),
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].deferred == ["prerequisites.md"]
        assert file.tasks[1].deferred == ["other.md"]


class TestAfterPreservesOtherAttributes:
    def test_deferred_task_keeps_priority(self):
        file = MarkdownFile(
            source_string="- [ ] **urgent deferred task** @after",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].priority == Priority.HIGH
        assert file.tasks[0].deferred == []

    def test_deferred_task_keeps_state(self):
        file = MarkdownFile(
            source_string="- [/] in progress but deferred @after",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].state == State.IN_PROGRESS
        assert file.tasks[0].deferred == []

    def test_completed_task_can_be_deferred(self):
        file = MarkdownFile(
            source_string="- [X] done but was deferred @after",
            today=date(2025, 1, 1),
        )
        assert file.tasks[0].state == State.COMPLETE
        assert file.tasks[0].deferred == []


class TestFilterDeferredBasic:
    def test_non_deferred_tasks_always_shown(self):
        file = MarkdownFile(
            source_string="- [ ] normal task",
            today=date(2025, 1, 1),
        )
        data = [(file, file.tasks)]
        result = filter_deferred(data)
        assert len(result) == 1
        assert len(result[0][1]) == 1
        assert result[0][1][0].text == "normal task"

    def test_bare_after_hidden_when_incomplete_tasks_exist(self):
        file = MarkdownFile(
            source_string=dedent("""\
                - [ ] normal task
                - [ ] deferred task @after
            """),
            today=date(2025, 1, 1),
        )
        data = [(file, file.tasks)]
        result = filter_deferred(data)
        assert len(result[0][1]) == 1
        assert result[0][1][0].text == "normal task"

    def test_bare_after_shown_when_all_complete(self):
        file = MarkdownFile(
            source_string=dedent("""\
                - [X] done task
                - [ ] deferred task @after
            """),
            today=date(2025, 1, 1),
        )
        data = [(file, file.tasks)]
        result = filter_deferred(data)
        assert len(result[0][1]) == 2

    def test_bare_after_shown_when_all_cancelled(self):
        file = MarkdownFile(
            source_string=dedent("""\
                - [#] cancelled task
                - [ ] deferred task @after
            """),
            today=date(2025, 1, 1),
        )
        data = [(file, file.tasks)]
        result = filter_deferred(data)
        assert len(result[0][1]) == 2

    def test_bare_after_hidden_when_blocked_exists(self):
        file = MarkdownFile(
            source_string=dedent("""\
                - [<] blocked task
                - [ ] deferred task @after
            """),
            today=date(2025, 1, 1),
        )
        data = [(file, file.tasks)]
        result = filter_deferred(data)
        assert len(result[0][1]) == 1
        assert result[0][1][0].text == "blocked task"

    def test_bare_after_hidden_when_in_progress_exists(self):
        file = MarkdownFile(
            source_string=dedent("""\
                - [/] in progress task
                - [ ] deferred task @after
            """),
            today=date(2025, 1, 1),
        )
        data = [(file, file.tasks)]
        result = filter_deferred(data)
        assert len(result[0][1]) == 1
        assert result[0][1][0].text == "in progress task"


class TestFilterDeferredAcrossFiles:
    def test_bare_after_considers_all_files(self):
        file1 = MarkdownFile(
            source_string="- [ ] task in file 1",
            path="file1.md",
            today=date(2025, 1, 1),
        )
        file2 = MarkdownFile(
            source_string="- [ ] deferred task @after",
            path="file2.md",
            today=date(2025, 1, 1),
        )
        data = [(file1, file1.tasks), (file2, file2.tasks)]
        result = filter_deferred(data)
        assert len(result[0][1]) == 1
        assert len(result[1][1]) == 0

    def test_bare_after_shown_when_all_files_complete(self):
        file1 = MarkdownFile(
            source_string="- [X] done in file 1",
            path="file1.md",
            today=date(2025, 1, 1),
        )
        file2 = MarkdownFile(
            source_string="- [ ] deferred task @after",
            path="file2.md",
            today=date(2025, 1, 1),
        )
        data = [(file1, file1.tasks), (file2, file2.tasks)]
        result = filter_deferred(data)
        assert len(result[1][1]) == 1


class TestFilterDeferredWithFileDependencies:
    def test_after_file_hidden_when_dependency_incomplete(self):
        prereq = MarkdownFile(
            source_string="- [ ] prerequisite task",
            path="prereq.md",
            today=date(2025, 1, 1),
        )
        dependent = MarkdownFile(
            source_string="- [ ] depends on prereq @after prereq.md",
            path="dependent.md",
            today=date(2025, 1, 1),
        )
        data = [(prereq, prereq.tasks), (dependent, dependent.tasks)]
        result = filter_deferred(data)
        assert len(result[0][1]) == 1
        assert len(result[1][1]) == 0

    def test_after_file_shown_when_dependency_complete(self):
        prereq = MarkdownFile(
            source_string="- [X] prerequisite task",
            path="prereq.md",
            today=date(2025, 1, 1),
        )
        dependent = MarkdownFile(
            source_string="- [ ] depends on prereq @after prereq.md",
            path="dependent.md",
            today=date(2025, 1, 1),
        )
        data = [(prereq, prereq.tasks), (dependent, dependent.tasks)]
        result = filter_deferred(data)
        assert len(result[1][1]) == 1

    def test_after_file_matches_basename(self):
        prereq = MarkdownFile(
            source_string="- [X] prerequisite task",
            path="subdir/prereq.md",
            today=date(2025, 1, 1),
        )
        dependent = MarkdownFile(
            source_string="- [ ] depends on prereq @after prereq.md",
            path="dependent.md",
            today=date(2025, 1, 1),
        )
        data = [(prereq, prereq.tasks), (dependent, dependent.tasks)]
        result = filter_deferred(data)
        assert len(result[1][1]) == 1

    def test_after_multiple_files_all_must_be_complete(self):
        file1 = MarkdownFile(
            source_string="- [X] done in file 1",
            path="stage1.md",
            today=date(2025, 1, 1),
        )
        file2 = MarkdownFile(
            source_string="- [ ] incomplete in file 2",
            path="stage2.md",
            today=date(2025, 1, 1),
        )
        dependent = MarkdownFile(
            source_string="- [ ] needs both @after stage1.md stage2.md",
            path="stage3.md",
            today=date(2025, 1, 1),
        )
        data = [
            (file1, file1.tasks),
            (file2, file2.tasks),
            (dependent, dependent.tasks),
        ]
        result = filter_deferred(data)
        assert len(result[2][1]) == 0

    def test_after_multiple_files_shown_when_all_complete(self):
        file1 = MarkdownFile(
            source_string="- [X] done in file 1",
            path="stage1.md",
            today=date(2025, 1, 1),
        )
        file2 = MarkdownFile(
            source_string="- [X] done in file 2",
            path="stage2.md",
            today=date(2025, 1, 1),
        )
        dependent = MarkdownFile(
            source_string="- [ ] needs both @after stage1.md stage2.md",
            path="stage3.md",
            today=date(2025, 1, 1),
        )
        data = [
            (file1, file1.tasks),
            (file2, file2.tasks),
            (dependent, dependent.tasks),
        ]
        result = filter_deferred(data)
        assert len(result[2][1]) == 1


class TestCheckDependencies:
    def test_circular_dependency_raises_error(self):
        file1 = MarkdownFile(
            source_string="- [ ] task @after file2.md",
            path="file1.md",
            today=date(2025, 1, 1),
        )
        file2 = MarkdownFile(
            source_string="- [ ] task @after file1.md",
            path="file2.md",
            today=date(2025, 1, 1),
        )
        with pytest.raises(CircularDependencyError):
            check_dependencies([file1, file2])

    def test_three_way_circular_dependency(self):
        file1 = MarkdownFile(
            source_string="- [ ] task @after file3.md",
            path="file1.md",
            today=date(2025, 1, 1),
        )
        file2 = MarkdownFile(
            source_string="- [ ] task @after file1.md",
            path="file2.md",
            today=date(2025, 1, 1),
        )
        file3 = MarkdownFile(
            source_string="- [ ] task @after file2.md",
            path="file3.md",
            today=date(2025, 1, 1),
        )
        with pytest.raises(CircularDependencyError):
            check_dependencies([file1, file2, file3])

    def test_self_reference_raises_error(self):
        file1 = MarkdownFile(
            source_string="- [ ] task @after file1.md",
            path="file1.md",
            today=date(2025, 1, 1),
        )
        with pytest.raises(CircularDependencyError):
            check_dependencies([file1])

    def test_no_error_when_no_cycles(self):
        file1 = MarkdownFile(
            source_string="- [ ] task",
            path="file1.md",
            today=date(2025, 1, 1),
        )
        file2 = MarkdownFile(
            source_string="- [ ] task @after file1.md",
            path="file2.md",
            today=date(2025, 1, 1),
        )
        check_dependencies([file1, file2])
