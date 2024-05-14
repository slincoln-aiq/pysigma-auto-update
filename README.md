# Update Pysigma Version

This GitHub Action automatically updates the pinned version of Pysigma in your `pyproject.toml` file and handles semantic versioning. It ensures that your project always uses the latest compatible version of Pysigma, and only creates a new release if all tests pass.

## Prerequisites

- Make sure you have a `pyproject.toml` file with Poetry as your dependency manager.
- Ensure your repository has a `tests` folder with test cases that validate your project.

## Inputs

- `dry_run`: Optional. Set to `true` to run the workflow without creating tags or releases. Default is `false`.

## Example Usage

To use this action, create a workflow file in your repository (e.g., `.github/workflows/update-pysigma.yml`) with the following content:

```yaml
name: Update Pysigma Version

on:
  schedule:
    - cron: '0 0 * * *'  # Adjust the schedule as needed
  workflow_dispatch:

jobs:
  update_pysigma:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Use Update Pysigma Version action
        uses: your-username/your-action-repo@v1
        with:
          dry_run: false
```

You can adjust the cron schedule to control how often the action runs. The workflow_dispatch trigger allows you to manually trigger the workflow from the GitHub Actions tab in your repository.

## Detailed Workflow

1. Set up Python: Sets up a Python environment.
2. Install Poetry: Installs Poetry for dependency management.
3. Install dependencies: Installs all dependencies using Poetry.
4. Run update script: Executes the script to check for and apply Pysigma version updates.
5. Commit changes: Commits and pushes changes to pyproject.toml if updates were made.
6. Run tests: Runs your project tests to ensure everything works with the new version.
7. Determine new version tag: Calculates the new version tag based on the latest tag.
8. Tag and push: Creates and pushes a new tag if all tests pass.
9. Create GitHub release: Creates a new GitHub release using the new tag. 

## Contributing
We welcome contributions! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request. Please make sure to follow our code of conduct.

## License
This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
