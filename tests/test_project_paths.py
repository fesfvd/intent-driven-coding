import tempfile
import unittest
from pathlib import Path

from _project_paths import assert_test_project_path


ROOT = Path(__file__).resolve().parents[1]


class TestProjectPaths(unittest.TestCase):
    def test_accepts_temporary_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "project"
            assert_test_project_path(project, temp_dir)

    def test_rejects_repository_root_and_child(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            for project in (ROOT, ROOT / "tests" / "fixture"):
                with self.subTest(project=project), self.assertRaises(AssertionError):
                    assert_test_project_path(project, temp_dir)

    def test_rejects_path_outside_explicit_temporary_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as other_dir:
            with self.assertRaises(AssertionError):
                assert_test_project_path(Path(other_dir) / "project", temp_dir)

    def test_rejects_symlink_alias_to_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            alias = Path(temp_dir) / "alias"
            try:
                alias.symlink_to(ROOT, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"directory symlinks unavailable: {exc}")
            for project in (alias, alias / "tests" / "fixture"):
                with self.subTest(project=project), self.assertRaises(AssertionError):
                    assert_test_project_path(project, temp_dir)

    def test_rejects_temporary_root_alias_to_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            alias = Path(temp_dir) / "alias"
            try:
                alias.symlink_to(ROOT, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"directory symlinks unavailable: {exc}")
            with self.assertRaises(AssertionError):
                assert_test_project_path(alias / "project", alias)


if __name__ == "__main__":
    unittest.main()
