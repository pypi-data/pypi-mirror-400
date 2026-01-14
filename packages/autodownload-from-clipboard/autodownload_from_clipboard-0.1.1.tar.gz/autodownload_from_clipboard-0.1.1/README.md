# autodownload-from-clipboard 🚀

## Quick Start: Run the Project with UV

```bash
uvx autodownload-from-clipboard
```

# Project description

An executable tool to automatically download videos and images from urls in the clipboard

# Template features

> Please make sure that everything is setup: [See Initial setup section below](#initial-setup)

**✨ Key Features:**

1. **Automatic Release Workflow:** 🚦
   Merging a pull request **automatically creates a release PR**—no manual steps required.

2. **One-Click Publishing:** 🚀
   Merging the release PR **builds & uploads artifacts** to both **PyPI and GitHub**, and **updates the changelog**.

3. **Zero-setup Development:** 🔄
   Powered by **Astral UV**, your **dev environment & all dependencies are fully managed**—no virtualenv or pip install needed.

4. **Continuous Testing:** 🧪
   **Unit tests run automatically** on **every pull request** to catch issues early.

5. **Automated Code Quality:** 🧹
   **Pre-commit hooks** enforce **code quality** and **style validation** before anything merges.

6. **Conventional Commits Required:** 📝
   **PR titles must follow [Conventional Commit](https://www.conventionalcommits.org/) standards** for clear, automated changelogs and semantic versioning.

7. **Easy Code Quality Checks:** ✅
   Local pre-commit hooks keep your code clean and consistent.
   * **Activate or deactivate:** 🔛🔚

     ```bash
     uv run pre-commit install    # enable hooks
     uv run pre-commit uninstall  # disable hooks
     ```

   * **Run all checks manually:** 🏃‍♂️

     ```bash
     uv run pre-commit run --all-files
     ```

     * *(the command is in `./precommit.sh`/ `./precommit.bat`)*

Once the setup is finished, the main entrypoint of this project (`app/main.py:main`) can be called from every computer which has `uv`, via the following command:

```bash
uvx autodownload-from-clipboard
```

It can also be called locally by calling:

```bash
uvx LOCAL_PATH/autodownload-from-clipboard
```

# Initial setup

> ⚠️ **IMPORTANT SETUP REQUIRED**
>
> Some essential configurations for automated releases and PyPI integration require using the GitHub and PyPi web interfaces. Please follow the steps below in your browser to complete the setup.

## Just after the cookiecutter has done his job, create the Github repo

* Repository name: autodownload-from-clipboard
* Description: An executable tool to automatically download videos and images from urls in the clipboard

Get to the local project:

```bash
git branch -M main
git remote add origin git@github.com:DSestu/autodownload-from-clipboard.git
git push -u origin main
```

## Enable GH actions to create PR's

To enable automatic Pull Requests from release-please, you'll need to grant GitHub Actions permission to create and approve pull requests:

1. Navigate to your repository on GitHub.
2. Go to **Settings** > **Actions** > **General**.
3. Scroll down to **Workflow permissions**.
4. Select **Allow GitHub Actions to create and approve pull requests**.

Next steps:

* In your repository's commit history, locate the "Cookiecutter initial commit" and copy its full commit SHA (use the copy icon at the end of the line).
* Open `release-please-config.json`, find the `bootstrap-sha` field, and replace its value with the SHA you just copied. Commit this change.

Finally, ensure your repository has at least one release tag. Create a release from the first commit and tag it as `0.1.0`.

> The release please will be triggered after the first PR merge.

## Setup publishing to Pypi

## Configure Publishing to PyPI

To enable publishing to PyPI via GitHub Actions, follow these steps:

1. **Set up GitHub Environment:**
   * In your GitHub repository, go to **Settings** > **Environments**.
   * Click **New environment** and name it `pypi`.

2. **Configure PyPI Publisher:**
   * Log in to your [PyPI account](https://pypi.org/).
   * Go to "Account settings" > "Publishing" and click "Add a new publisher".
   * Choose "GitHub" as the integration type.
   * Follow the instructions to link your repository and grant the required permissions.
   * Select or specify the workflow file as `release_please.yml` (or the workflow you use for releases).
   * Ensure the environment name (`pypi`) matches exactly—this tells the workflow and PyPI which environment to expect.

3. **Verify Package Name Consistency:**
   * Make sure the package name in your `pyproject.toml` file matches exactly with your project name on PyPI. This is critical for successful publishing.

By following these steps, you'll enable automated publishing of your package to PyPI whenever a release is created via GitHub Actions.

## Advice

To improve the default pull request workflow experience, update your repository's settings as follows:

1. Go to your repository's **Settings**.
2. Scroll down to the **Pull requests** section.
3. Disable **Allow merge commits** & **Allow rebase merging**
4. Keep **Allow squash merging**, and change the default commit message to **Pull request title**

This will ensure your merge commits use clear, descriptive titles from pull requests instead of the default text, and keep changelogs concise.
