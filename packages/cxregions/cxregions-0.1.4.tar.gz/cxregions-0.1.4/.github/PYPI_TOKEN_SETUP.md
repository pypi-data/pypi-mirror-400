# Setting up PyPI API Token for GitHub Actions

This guide explains how to set up a PyPI API token as a GitHub secret for automated package publishing.

## Generate a PyPI API Token

1. Log in to your PyPI account at https://pypi.org/
2. Go to your account settings by clicking on your username in the top right corner
3. Navigate to "API tokens" in the left sidebar
4. Click "Add API token"
5. Give your token a name (e.g., "GitHub Actions")
6. Set the scope to "Entire account" or limit it to the `cxregions` project
7. Click "Create token"
8. Copy the token value - **IMPORTANT**: This is the only time you'll see the token value!

## Add the Token to GitHub Secrets

1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. For the name, enter `PYPI_API_TOKEN`
6. For the value, paste the PyPI API token you copied earlier
7. Click "Add secret"

## Verification

The GitHub Actions workflow is now configured to use this token when publishing to PyPI. The workflow will:

1. Run tests on every push to main and pull requests
2. If tests pass and the event is a push to main, it will build and publish the package to PyPI
3. The version will be determined from git tags (if a tag is pushed) or generated automatically

No further configuration is needed for the workflow to function properly.