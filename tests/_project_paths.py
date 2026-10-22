from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def assert_not_repository_path(project: str | Path) -> None:
    destination = Path(project).resolve()
    if destination == REPOSITORY_ROOT or destination.is_relative_to(REPOSITORY_ROOT):
        raise AssertionError(f"project is inside the repository: {destination}")


def assert_test_project_path(project: str | Path, temporary_root: str | Path) -> None:
    destination = Path(project).resolve()
    sandbox = Path(temporary_root).resolve()
    assert_not_repository_path(destination)
    if sandbox == REPOSITORY_ROOT or sandbox.is_relative_to(REPOSITORY_ROOT):
        raise AssertionError(f"temporary root is inside the repository: {sandbox}")
    if destination != sandbox and not destination.is_relative_to(sandbox):
        raise AssertionError(f"project is outside the temporary root: {destination}")
