# Set the default recipe to list all available commands
@default:
    @just --list

# Set the uv run command
uv := "uv run"

#Set the uv command to run a tool
uv-tool := "uv tool run"

# Run Ruff linking
@lint:
    {{uv-tool}} ruff check

# Run Ruff formatting
@format:
    {{uv-tool}} ruff format

# Sync the package
@sync:
    uv sync --all-extras

# Sync the package
@sync-up:
    uv sync --all-extras --upgrade

# Lock the package version
@lock:
    uv lock

# Build the package
@build:
    uv build

# Publish the package - this requires a $HOME/.pypirc file with your credentials
@publish:
      rm -rf ./dist/*
      uv build
      {{uv-tool}} twine check dist/*
      {{uv-tool}} twine upload dist/*

# Upgrade pre-commit hooks
@pc-up:
    {{uv-tool}} pre-commit autoupdate

# Run pre-commit hooks
@pc-run:
    {{uv-tool}} pre-commit run --all-files

# Use BumpVer to increase the patch version number. Use just bump -d to view a dry-run.
@bump *ARGS:
    uv run bumpver update --patch {{ ARGS }}
    uv sync

# Use BumpVer to increase the minor version number. Use just bump -d to view a dry-run.
@bump-minor *ARGS:
    uv run bumpver update --minor {{ ARGS }}
    uv sync

# Use BumpVer to increase the major version number. Use just bump -d to view a dry-run.
@bump-major *ARGS:
    uv run bumpver update --major {{ ARGS }}
    uv sync
