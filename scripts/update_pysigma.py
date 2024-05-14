import sys

import requests
import toml
from packaging.specifiers import SpecifierSet
from packaging.version import parse, Version


def get_latest_release(repo_name: str) -> Version:
    """Get the latest release version from the GitHub repository.

    Args:
        repo_name: The GitHub repository name in the format `owner/repo`.

    Returns:
        The latest release version.
    """
    url = f"https://api.github.com/repos/{repo_name}/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    return parse(response.json()["tag_name"].lstrip("v"))


def preprocess_specifier(specifier: str) -> str:
    """Preprocess the specifier to handle the caret operator.

    Args:
        specifier: The specifier string.

    Returns:
        The preprocessed specifier string.
    """
    if specifier.startswith("^"):
        version = specifier[1:]
        major, minor, _ = version.split(".")
        upper_bound = f"<{int(major) + 1}.0.0"
        return f">={version}, {upper_bound}"
    return specifier


def merge_specifiers(current_specifiers: SpecifierSet, latest_version: str) -> SpecifierSet:
    """Merge the current specifiers with the latest version.

    Args:
        current_specifiers: The current specifiers.
        latest_version: The latest version.

    Returns:
        The new specifiers set.
    """
    new_specifiers = []
    has_upper_bound = False
    for spec in current_specifiers:
        if spec.operator in ("<=", "<"):
            has_upper_bound = True
            if spec.operator == "<=":
                new_specifiers.append(f"<= {latest_version}")
            else:
                new_specifiers.append(f"<= {latest_version}")
        else:
            new_specifiers.append(str(spec))
    if not has_upper_bound:
        new_specifiers.append(f"<= {latest_version}")
    # Remove redundant specifiers
    new_specifiers_set = SpecifierSet(", ".join(new_specifiers))
    return new_specifiers_set


def read_pyproject_version(path: str = "pyproject.toml") -> SpecifierSet:
    """Read the current version of pysigma from the pyproject.toml file.

    Args:
        path: The path to the pyproject.toml file.

    Returns:
        The current specifiers set.
    """
    with open(path, "r") as f:
        pyproject_data = toml.load(f)
    specifiers = pyproject_data["tool"]["poetry"]["dependencies"]["pysigma"]
    # Handle multiple specifiers
    if "," in specifiers:
        return SpecifierSet(", ".join(preprocess_specifier(spec) for spec in specifiers.split(",")))
    return SpecifierSet(preprocess_specifier(specifiers))


def update_pyproject_version(path: str, new_specifier: SpecifierSet):
    """Update the pyproject.toml file with the new pysigma specifier.

    Args:
        path: The path to the pyproject.toml file.
        new_specifier: The new specifiers set.
    """

    with open(path, "r") as f:
        pyproject_data = toml.load(f)
    pyproject_data["tool"]["poetry"]["dependencies"]["pysigma"] = str(new_specifier)
    with open(path, "w") as f:
        toml.dump(pyproject_data, f)


def main(dry_run: bool = False):
    """Check if the pySigma version in pyproject.toml is up-to-date. Return code 1 if an update is required.


    Args:
        dry_run: Whether to perform a dry run without updating the file.
    """
    repo_name = "SigmaHQ/pySigma"
    pyproject_path = "pyproject.toml"

    latest_version = get_latest_release(repo_name)
    current_specifiers = read_pyproject_version(pyproject_path)

    if latest_version not in current_specifiers:
        new_specifiers_set = merge_specifiers(current_specifiers, latest_version)
        if not dry_run:
            update_pyproject_version(pyproject_path, new_specifiers_set)
            print(f"Updated pyproject.toml to include {latest_version}")
            sys.exit(1)  # Exit with code 1 to indicate update

    print("No update required.")
    sys.exit(0)  # Exit with code 0 to indicate no update


if __name__ == "__main__":
    dry_run = sys.argv[1].lower() == "true" if len(sys.argv) > 1 else False
    main(dry_run)
