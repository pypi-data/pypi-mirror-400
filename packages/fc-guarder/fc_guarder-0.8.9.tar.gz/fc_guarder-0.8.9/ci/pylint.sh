#!/usr/bin/env bash

set -x
set -e  # Exit immediately if any command fails

# Define common disable flags
DISABLE_FLAGS="line-too-long,too-many-locals,too-many-statements,too-many-branches,too-many-arguments,broad-except,too-many-return-statements,bare-except"

# Define folders to exclude from general pylint run
EXCLUDE_FOLDERS=(docker doc .venv fc_agent fc_mcp)

# Build the exclude path expression
EXCLUDE_PATHS=""
for folder in "${EXCLUDE_FOLDERS[@]}"; do
    if [ -n "$EXCLUDE_PATHS" ]; then
        EXCLUDE_PATHS="$EXCLUDE_PATHS -o -path ./$folder"
    else
        EXCLUDE_PATHS="-path ./$folder"
    fi
done

# Run pylint for fc_agent with additional disables
find ./fc_agent -name "*.py" -print | xargs pylint --disable="$DISABLE_FLAGS"

# Run pylint for fc_mcp with additional disables
find ./fc_mcp -name "*.py" -print | xargs pylint --disable="$DISABLE_FLAGS"

# Run pylint for other files normally
find . \( $EXCLUDE_PATHS \) -prune -o -name "*.py" -print | xargs pylint
